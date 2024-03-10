import typing as t
from dataclasses import dataclass, field
from ragas.llms.prompt import Prompt
from ragas.testset.evolutions import ComplexEvolution, CurrentNodes, EvolutionOutput, DataRow
import logging
from ragas.testset.docstore import Node
from ragas.exceptions import MaxRetriesExceeded
from ragas.llms.json_load import json_loader
import numpy as np


logger = logging.getLogger(__name__)

conversational_question_prompt = Prompt(
    name="conversation_question",
    instruction="""Reformat the provided question into two separate questions as if it were to be part of a conversation. Each question should focus on a specific aspect or subtopic related to the original question.
    Follow the rules given below while rewriting the question.
        1. The rewritten question should not be longer than 25 words. Use abbreviation wherever possible.
        2. The rewritten question must be reasonable and must be understood and responded by humans.
        3. The rewritten question must be fully answerable from information present context.
        4. phrases like 'provided context','according to the context?',etc are not allowed to appear in the question.""",
    examples=[
        {
            "question": "What are the advantages and disadvantages of remote work?",
            "output": {
                "first_question": "What are the benefits of remote work?",
                "second_question": "On the flip side, what challenges are encountered when working remotely?",
            },
        }
    ],
    input_keys=["question"],
    output_key="output",
    output_type="json",
    language="english",
)

continue_conversation_prompt = Prompt(
    name="continue_conversation",
    instruction="""""",
    examples=[
        {
            "question": "What are the advantages and disadvantages of remote work?",
            "output": {
                "first_question": "What are the benefits of remote work?",
                "second_question": "On the flip side, what challenges are encountered when working remotely?",
            },
        }
    ],
    input_keys=["question"],
    output_key="output",
    output_type="json",
    language="english",
)


@dataclass
class ConversationalEvolution(ComplexEvolution):
    conversational_question_prompt: Prompt = field(
        default_factory=lambda: conversational_question_prompt
    )

    async def generate_datarow(
        self,
        conversation_history: list,
        conversation_nodes: list,
        evolution_type: str,
    ):
        assert self.generator_llm is not None, "generator_llm cannot be None"
        
        node_content = [
            f"{i+1}\t{n.page_content}" for i, n in enumerate(current_nodes.nodes)
        ]
        results = await self.generator_llm.generate(
            prompt=self.find_relevant_context_prompt.format(
                question=question, contexts=node_content
            )
        )
        relevant_contexts_result = await json_loader.safe_load(
            results.generations[0][0].text.strip(), llm=self.generator_llm
        )
        relevant_context_indices = (
            relevant_contexts_result.get("relevant_contexts", None)
            if isinstance(relevant_contexts_result, dict)
            else None
        )
        if relevant_context_indices is None:
            relevant_context = CurrentNodes(
                root_node=current_nodes.root_node, nodes=current_nodes.nodes
            )
        else:
            selected_nodes = [
                current_nodes.nodes[i - 1]
                for i in relevant_context_indices
                if i - 1 < len(current_nodes.nodes)
            ]
            relevant_context = (
                CurrentNodes(root_node=selected_nodes[0], nodes=selected_nodes)
                if selected_nodes
                else current_nodes
            )

        merged_nodes = self.merge_nodes(relevant_context)
        results = await self.generator_llm.generate(
            prompt=self.question_answer_prompt.format(
                question=question, context=merged_nodes.page_content
            )
        )
        answer = await json_loader.safe_load(
            results.generations[0][0].text.strip(), self.generator_llm
        )
        answer = answer if isinstance(answer, dict) else {}
        logger.debug("answer generated: %s", answer)
        answer = (
            np.nan if answer.get("verdict") == "-1" else answer.get("answer", np.nan)
        )

        return DataRow(
            question=question.strip('"'),
            contexts=[n.page_content for n in relevant_context.nodes],
            ground_truth=answer,
            evolution_type=evolution_type,
        )

    async def evolve(self, current_nodes: CurrentNodes, job_to_be_done: str) -> DataRow:
        # init tries with 0 when first called
        current_tries = 0
        (
            convo_history,
            convo_nodes,
            evolution_type,
        ) = await self._aevolve(current_tries, current_nodes, job_to_be_done)

        return await self.generate_datarow(
            conversation_history=convo_history,
            conversation_nodes=convo_nodes,
            evolution_type=evolution_type,
        )

    async def _aevolve(
        self, current_tries: int, current_nodes: CurrentNodes, job_to_be_done: str
    ) -> EvolutionOutput:
        assert self.docstore is not None, "docstore cannot be None"
        assert self.generator_llm is not None, "generator_llm cannot be None"
        assert self.question_filter is not None, "question_filter cannot be None"
        assert self.se is not None, "simple evolution cannot be None"
        starting_question, current_nodes, _ = await self.se._aevolve(
            current_tries, current_nodes
        )
        logger.debug(
            "[ConversationalEvolution] starting questions generated: %s", starting_question
        )
        json_results = await json_loader.safe_load(starting_question, llm=self.generator_llm)
        json_results = json_results if isinstance(json_results, dict) else {}
        print("simple question results: %s", json_results)
        question_1 = json_results.get("first_question", "")
        question_2 = json_results.get("second_question", "")
        # three turn convo so we continue conversations twice
        question_1_1, question_1_2, nodes_1 = await self.continue_convo(current_tries, current_nodes, question_1, job_to_be_done)
        question_2_1, question_2_2, nodes_2 = await self.continue_convo(current_tries, current_nodes, question_2, job_to_be_done)
        question_1_1_1, question_1_1_2, nodes_1_1 = await self.continue_convo(current_tries, nodes_1, question_1_1, job_to_be_done)
        question_1_2_1, question_1_2_2, nodes_1_2 = await self.continue_convo(current_tries, nodes_1, question_1_2, job_to_be_done)
        question_2_1_1, question_2_1_2, nodes_2_1 = await self.continue_convo(current_tries, nodes_2, question_2_1, job_to_be_done)
        question_2_2_1, question_2_2_2, nodes_2_2 = await self.continue_convo(current_tries, nodes_2, question_2_2, job_to_be_done)
        conversation_history = [
            [question_1, question_1_1, question_1_1_1],
            [question_1, question_1_1, question_1_1_2],
            [question_1, question_1_2, question_1_2_1],
            [question_1, question_1_2, question_1_2_2],
            [question_2, question_2_1, question_2_1_1],
            [question_2, question_2_1, question_2_1_2],
            [question_2, question_2_2, question_2_2_1],
            [question_2, question_2_2, question_2_2_2],
        ]
        convo_nodes = [
            [current_nodes, nodes_1, nodes_1_1],
            [current_nodes, nodes_1, nodes_1_1],
            [current_nodes, nodes_1, nodes_1_2],
            [current_nodes, nodes_1, nodes_1_2],
            [current_nodes, nodes_2, nodes_2_1],
            [current_nodes, nodes_2, nodes_2_1],
            [current_nodes, nodes_2, nodes_2_2],
            [current_nodes, nodes_2, nodes_2_2],
        ]
        return conversation_history, convo_nodes, "conversational"

    async def continue_convo(self, current_tries: int, current_nodes: CurrentNodes, question:str, job_to_be_done: str):
        # find a similar node and generate a question based on both
        merged_node = self.merge_nodes(current_nodes)
        similar_node = self.docstore.get_similar(merged_node, top_k=1)
        if similar_node == []:
            # retry
            new_random_nodes = self.docstore.get_random_nodes(k=1)
            current_nodes = CurrentNodes(
                root_node=new_random_nodes[0], nodes=new_random_nodes
            )
            return await self.aretry_evolve(current_tries, current_nodes, job_to_be_done)
        else:
            assert isinstance(similar_node[0], Node), "similar_node must be a Node"
            current_nodes.nodes.append(similar_node[0])
        prompt = self.conversational_question_prompt.format(
            question=question,
        )
        results = await self.generator_llm.generate(prompt=prompt)
        results = results.generations[0][0].text.strip()
        json_results = await json_loader.safe_load(results, llm=self.llm)
        json_results = json_results if isinstance(json_results, dict) else {}
        logger.debug("simple question results: %s", json_results)
        question_1 = json_results.get("first_question", "")
        question_2 = json_results.get("second_question", "")
        is_valid_question_1, feedback_1 = await self.question_filter.filter(question_1)
        is_valid_question_2, feedback_2 = await self.question_filter.filter(question_2)
        if not is_valid_question_1:
            # get more context to rewrite question
            question_1, current_nodes = await self.fix_invalid_question(
                question_1, current_nodes, feedback_1
            )
            logger.info("rewritten question: %s", question_1)
            is_valid_question_1, _ = await self.question_filter.filter(question_1)
        if not is_valid_question_2:
            # get more context to rewrite question
            question_2, current_nodes = await self.fix_invalid_question(
                question_2, current_nodes, feedback_2
            )
            logger.info("rewritten question: %s", question_2)
            is_valid_question_2, _ = await self.question_filter.filter(question_2)
        if not is_valid_question_1 and not is_valid_question_2:
            # retry
            current_nodes = self.se._get_new_random_node()
            return await self.aretry_evolve(current_tries, current_nodes, job_to_be_done)
        return question_1, question_2, current_nodes
    
    def __hash__(self):
        return hash(self.__class__.__name__)
    
    async def aretry_evolve(
        self,
        current_tries: int,
        current_nodes: CurrentNodes,
        job_to_be_done: str,
        update_count: bool = True,
    ) -> EvolutionOutput:
        if update_count:
            current_tries += 1
        logger.info("retrying evolution: %s times", current_tries)
        if current_tries > self.max_tries:
            # TODO: make this into a custom exception
            raise MaxRetriesExceeded(self)
        return await self._aevolve(current_tries, current_nodes, job_to_be_done)

    def adapt(self, language: str, cache_dir: t.Optional[str] = None) -> None:
        super().adapt(language, cache_dir)
        self.conversational_question_prompt = self.conversational_question_prompt.adapt(
            language, self.generator_llm, cache_dir
        )

    def save(self, cache_dir: t.Optional[str] = None) -> None:
        super().save(cache_dir)
        self.conversational_question_prompt.save(cache_dir)

conversation=ConversationalEvolution()