import os

from typing import Any, Optional
from unittest.mock import patch

import pydantic
import pytest

from autopr.actions.utils.prompt_context import PromptContext, PromptContextEntry
from autopr.models.executable import ContextDict, ExecutableId
from autopr.services.platform_service import DummyPlatformService
from autopr.tests.mock_openai import mock_openai

from autopr.actions.find_todos import TodoLocation, Todo

from autopr.tests.utils import run_action_manually

@patch.object(DummyPlatformService, "get_file_url", return_value="github.com")
@pytest.mark.parametrize(
    "inputs, expected_outputs, repo_resource",
    [
        (
            {},
            {
                "todos": [
                    Todo(
                        task='FIXME does nice syntax highlighting for tracebacks, but should be made configurable',
                        locations=[
                            TodoLocation(
                                filepath='todos.py', 
                                start_line=3, 
                                end_line=3, 
                                url='github.com'
                            )
                        ]
                    ),
                    Todo(
                        task="FIXME: PART1: THIS SHOULD GET RETURNED PART2: THIS SHOULD GET RETURNED",
                        locations=[
                            TodoLocation(
                                filepath='subfolder1/fixme-example.py', 
                                start_line=1, 
                                end_line=2,
                                url="github.com",
                            ),
                            TodoLocation(
                                filepath='subfolder1/fixme-example.py', 
                                start_line=13, 
                                end_line=14,
                                url="github.com",
                            )
                        ]
                    ),
                    Todo(
                        task="FIXME: PART1:this is whatever",
                        locations=[
                            TodoLocation(
                                filepath='subfolder1/fixme-example.py', 
                                start_line=4, 
                                end_line=4,
                                url="github.com",
                            )
                        ]
                    ),
                    Todo(
                        task="TODO write a ... with #TOO or #FIXME in them ...",
                        locations=[
                            TodoLocation(
                                filepath='todos.py', 
                                start_line=1, 
                                end_line=1,
                                url="github.com"
                            )
                        ]
                    ),
                    Todo(
                        task="TODO: PART1: THIS SHOULD GET RETURNED PART2: THIS SHOULD GET RETURNED",
                        locations=[
                            TodoLocation(
                                filepath='subfolder1/todo-example.py',
                                start_line=1, 
                                end_line=2,
                                url="github.com",
                            ),
                            TodoLocation(
                                filepath='subfolder1/todo-example.py',
                                start_line=7,
                                end_line=8,
                                url="github.com",
                            )
                        ]
                    ),
                    Todo(
                        task="TODO: PART1:this is whatever",
                        locations=[
                            TodoLocation(
                                filepath='subfolder1/todo-example.py',
                                start_line=4,
                                end_line=4,
                                url="github.com",
                            )
                        ]
                    ),
                ]
            },
            "repo_with_todos",
        ),
        (
            {
                "comment": "//",
                "todo_keywords": ["TODO", "FIXME", "WHATEVER"],
            },
            {
                "todos": [
                    Todo(
                        task="FIXME: PART1: THIS SHOULD GET RETURNED PART2: THIS SHOULD GET RETURNED",
                        locations=[
                            TodoLocation(
                                filepath='subfolder1/fixme-example.js', 
                                start_line=1, 
                                end_line=2,
                                url="github.com",
                                ),
                            TodoLocation(
                                filepath='subfolder1/fixme-example.js', 
                                start_line=7, 
                                end_line=7,
                                url="github.com",
                                )
                        ],
                    ),
                    Todo(
                        task="WHATEVER: PART1: THIS SHOULD GET RETURNED",
                        locations=[
                            TodoLocation(
                                filepath='subfolder1/fixme-example.js', 
                                start_line=4, 
                                end_line=4,
                                url="github.com",
                                )
                            ]
                    )
                ]
            },
            "repo_with_todos",
        ),
        (
            {
                "comment": "//",
            },
            {
                "todos": [
                    Todo(
                        task="FIXME: PART1: THIS SHOULD GET RETURNED PART2: THIS SHOULD GET RETURNED",
                        locations=[
                            TodoLocation(
                                filepath='subfolder1/fixme-example.js', 
                                start_line=1,
                                end_line=2,
                                url="github.com",
                                ),
                            TodoLocation(
                                filepath='subfolder1/fixme-example.js', 
                                start_line=7, 
                                end_line=7,
                                url="github.com",
                                )
                            ],
                    )
                ]
            },
            "repo_with_todos",
        ),
        (
            {
                "comment": "€",
            },
            {
                "todos": []
            },
            "repo_with_todos",
        )
    ]
)
@pytest.mark.asyncio
async def test_actions(
    mocker,
    inputs: ContextDict,
    expected_outputs: dict[str, Any],
    repo_resource: Optional[str],
):
    mocker.patch(
        "openai.ChatCompletion.acreate",
        new=mock_openai,
    )
    outputs = await run_action_manually(
        action=ExecutableId("find_todos"),
        inputs=ContextDict(inputs),
        repo_resource=repo_resource
    )

    assert outputs == expected_outputs
