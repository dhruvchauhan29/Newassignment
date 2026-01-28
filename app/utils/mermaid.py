"""Mermaid diagram generation utilities."""
from typing import List


def generate_architecture_diagram(components: List[str]) -> str:
    """Generate a Mermaid architecture diagram.

    Args:
        components: List of component names

    Returns:
        Mermaid diagram code
    """
    diagram = "graph TB\n"
    diagram += "    Client[Client Application]\n"

    for i, component in enumerate(components):
        diagram += f"    C{i}[{component}]\n"
        diagram += f"    Client --> C{i}\n"

    return diagram


def generate_sequence_diagram(interactions: List[dict]) -> str:
    """Generate a Mermaid sequence diagram.

    Args:
        interactions: List of interaction dicts with 'from', 'to', 'message'

    Returns:
        Mermaid diagram code
    """
    diagram = "sequenceDiagram\n"

    for interaction in interactions:
        from_actor = interaction.get("from", "")
        to_actor = interaction.get("to", "")
        message = interaction.get("message", "")
        diagram += f"    {from_actor}->>{to_actor}: {message}\n"

    return diagram


def generate_flow_diagram(steps: List[str]) -> str:
    """Generate a Mermaid flow diagram.

    Args:
        steps: List of step names

    Returns:
        Mermaid diagram code
    """
    diagram = "flowchart TD\n"
    diagram += "    Start([Start])\n"

    for i, step in enumerate(steps):
        diagram += f"    S{i}[{step}]\n"
        if i == 0:
            diagram += f"    Start --> S{i}\n"
        else:
            diagram += f"    S{i-1} --> S{i}\n"

    diagram += f"    S{len(steps)-1} --> End([End])\n"

    return diagram
