"""Research database service for managing shared knowledge base."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ResearchDatabase:
    """Manages file-based research storage with YAML metadata."""

    def __init__(self, base_path: str = "research_database"):
        """
        Initialize research database manager.

        Args:
            base_path: Base directory for research storage
        """
        self.base_path = Path(base_path)
        self.sessions_path = self.base_path / "sessions"

        # Ensure base directories exist
        self.base_path.mkdir(exist_ok=True)
        self.sessions_path.mkdir(exist_ok=True)

    def create_session_directory(self, session_id: str, ticker: str) -> Path:
        """
        Create directory structure for a research session.

        Args:
            session_id: Unique session identifier
            ticker: Stock ticker symbol

        Returns:
            Path to session directory
        """
        session_dir = self.sessions_path / session_id / ticker

        # Create main directories
        session_dir.mkdir(parents=True, exist_ok=True)

        # Create agent-specific subdirectories
        agent_dirs = ["valuation", "strategic", "historical", "synthesis", "meta"]
        for agent_dir in agent_dirs:
            (session_dir / agent_dir).mkdir(exist_ok=True)

        # Create metadata files
        self._initialize_metadata_files(session_dir, session_id, ticker)

        logger.info(f"Created session directory structure: {session_dir}")
        return session_dir

    def _initialize_metadata_files(self, session_dir: Path, session_id: str, ticker: str) -> None:
        """Initialize metadata files for a new session."""
        meta_dir = session_dir / "meta"

        # Initialize file index
        file_index = {
            "session_id": session_id,
            "ticker": ticker,
            "created_at": datetime.now(UTC).isoformat(),
            "files": {},
        }
        self._write_yaml_file(meta_dir / "file_index.yaml", file_index)

        # Initialize cross references
        cross_references = {"session_id": session_id, "ticker": ticker, "references": []}
        self._write_yaml_file(meta_dir / "cross_references.yaml", cross_references)

        # Initialize agent activity
        agent_activity = {
            "session_id": session_id,
            "ticker": ticker,
            "agents": {
                "valuation_agent": {"status": "pending", "files": []},
                "strategic_agent": {"status": "pending", "files": []},
                "historian_agent": {"status": "pending", "files": []},
                "synthesis_agent": {"status": "pending", "files": []},
            },
        }
        self._write_yaml_file(meta_dir / "agent_activity.yaml", agent_activity)

    def write_research_file(
        self,
        session_id: str,
        ticker: str,
        agent_type: str,
        filename: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """
        Write a research file with YAML metadata header.

        Args:
            session_id: Session identifier
            ticker: Stock ticker
            agent_type: Type of agent (valuation, strategic, etc.)
            filename: Name of the file
            content: Research content
            metadata: Additional metadata

        Returns:
            Path to written file
        """
        session_dir = self.sessions_path / session_id / ticker
        agent_dir = session_dir / agent_type

        # Ensure directory exists
        agent_dir.mkdir(parents=True, exist_ok=True)

        # Prepare metadata
        if metadata is None:
            metadata = {}

        metadata.update(
            {
                "session_id": session_id,
                "ticker": ticker,
                "agent_type": agent_type,
                "created_at": datetime.now(UTC).isoformat(),
                "version": 1,
            }
        )

        # Create file with YAML header
        file_path = agent_dir / filename

        yaml_header = "---\n" + yaml.dump(metadata, default_flow_style=False) + "---\n\n"
        full_content = yaml_header + content

        file_path.write_text(full_content, encoding="utf-8")

        # Update file index
        session_dir = self.sessions_path / session_id / ticker
        relative_path = str(file_path.relative_to(session_dir))
        self._update_file_index(session_id, ticker, relative_path)

        # Update agent activity
        self._update_agent_activity(session_id, ticker, f"{agent_type}_agent", filename)

        logger.info(f"Wrote research file: {file_path}")
        return file_path

    def read_research_file(
        self, session_id: str, ticker: str, relative_path: str
    ) -> dict[str, Any]:
        """
        Read a research file and parse metadata.

        Args:
            session_id: Session identifier
            ticker: Stock ticker
            relative_path: Relative path to file from session directory

        Returns:
            Dictionary with 'metadata' and 'content' keys
        """
        file_path = self.sessions_path / session_id / ticker / relative_path

        if not file_path.exists():
            raise FileNotFoundError(f"Research file not found: {file_path}")

        content = file_path.read_text(encoding="utf-8")

        # Parse YAML header
        if content.startswith("---\n"):
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                main_content = parts[2]
                metadata = yaml.safe_load(yaml_content) or {}
            else:
                metadata = {}
                main_content = content
        else:
            metadata = {}
            main_content = content

        return {"metadata": metadata, "content": main_content.strip()}

    def get_session_files(self, session_id: str, ticker: str) -> list[dict[str, Any]]:
        """
        Get all research files for a session.

        Args:
            session_id: Session identifier
            ticker: Stock ticker

        Returns:
            List of file information dictionaries
        """
        file_index = self._read_file_index(session_id, ticker)
        if not file_index:
            return []

        files = []
        for relative_path, file_info in file_index.get("files", {}).items():
            try:
                file_data = self.read_research_file(session_id, ticker, relative_path)
                files.append(
                    {
                        "path": relative_path,
                        "metadata": file_data["metadata"],
                        "size": len(file_data["content"]),
                        "created_at": file_info.get("created_at"),
                    }
                )
            except Exception as e:
                logger.warning(f"Error reading file {relative_path}: {str(e)}")

        return files

    def get_agent_context(self, session_id: str, ticker: str, agent_type: str) -> dict[str, Any]:
        """
        Get all available context for an agent from previous research.

        Args:
            session_id: Session identifier
            ticker: Stock ticker
            agent_type: Type of requesting agent

        Returns:
            Dictionary with context from previous agents
        """
        context = {
            "session_id": session_id,
            "ticker": ticker,
            "requesting_agent": agent_type,
            "previous_research": {},
        }

        # Define agent dependencies (what each agent can read)
        agent_dependencies = {
            "valuation": [],  # First agent, no dependencies
            "strategic": ["valuation"],  # Reads valuation
            "historical": ["valuation", "strategic"],  # Reads both
            "synthesis": ["valuation", "strategic", "historical"],  # Reads all
        }

        available_agents = agent_dependencies.get(agent_type, [])

        for dep_agent in available_agents:
            agent_dir = self.sessions_path / session_id / ticker / dep_agent
            if agent_dir.exists():
                agent_files = []
                for file_path in agent_dir.glob("*.md"):
                    try:
                        file_data = self.read_research_file(
                            session_id,
                            ticker,
                            file_path.relative_to(self.sessions_path / session_id / ticker),
                        )
                        agent_files.append(file_data)
                    except Exception as e:
                        logger.warning(f"Error reading {file_path}: {str(e)}")

                context["previous_research"][dep_agent] = agent_files

        return context

    def add_cross_reference(
        self, session_id: str, ticker: str, source_file: str, target_file: str, relationship: str
    ) -> None:
        """
        Add a cross-reference between research files.

        Args:
            session_id: Session identifier
            ticker: Stock ticker
            source_file: Source file path
            target_file: Target file path
            relationship: Description of relationship
        """
        cross_refs = self._read_cross_references(session_id, ticker)
        if cross_refs:
            cross_refs["references"].append(
                {
                    "source": source_file,
                    "target": target_file,
                    "relationship": relationship,
                    "created_at": datetime.now(UTC).isoformat(),
                }
            )

            meta_dir = self.sessions_path / session_id / ticker / "meta"
            self._write_yaml_file(meta_dir / "cross_references.yaml", cross_refs)

    def _update_file_index(self, session_id: str, ticker: str, relative_path: str) -> None:
        """Update the file index with a new file."""
        file_index = self._read_file_index(session_id, ticker)
        if file_index:
            file_index["files"][relative_path] = {
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
            }

            meta_dir = self.sessions_path / session_id / ticker / "meta"
            self._write_yaml_file(meta_dir / "file_index.yaml", file_index)

    def _update_agent_activity(
        self, session_id: str, ticker: str, agent_name: str, filename: str
    ) -> None:
        """Update agent activity tracking."""
        activity = self._read_agent_activity(session_id, ticker)
        if activity and agent_name in activity["agents"]:
            activity["agents"][agent_name]["files"].append(
                {"filename": filename, "created_at": datetime.now(UTC).isoformat()}
            )
            activity["agents"][agent_name]["status"] = "active"

            meta_dir = self.sessions_path / session_id / ticker / "meta"
            self._write_yaml_file(meta_dir / "agent_activity.yaml", activity)

    def _read_file_index(self, session_id: str, ticker: str) -> dict[str, Any] | None:
        """Read the file index for a session."""
        file_path = self.sessions_path / session_id / ticker / "meta" / "file_index.yaml"
        return self._read_yaml_file(file_path)

    def _read_cross_references(self, session_id: str, ticker: str) -> dict[str, Any] | None:
        """Read cross references for a session."""
        file_path = self.sessions_path / session_id / ticker / "meta" / "cross_references.yaml"
        return self._read_yaml_file(file_path)

    def _read_agent_activity(self, session_id: str, ticker: str) -> dict[str, Any] | None:
        """Read agent activity for a session."""
        file_path = self.sessions_path / session_id / ticker / "meta" / "agent_activity.yaml"
        return self._read_yaml_file(file_path)

    def _read_yaml_file(self, file_path: Path) -> dict[str, Any] | None:
        """Read and parse a YAML file."""
        try:
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                return yaml.safe_load(content)
        except Exception as e:
            logger.error(f"Error reading YAML file {file_path}: {str(e)}")
        return None

    def _write_yaml_file(self, file_path: Path, data: dict[str, Any]) -> None:
        """Write data to a YAML file."""
        try:
            content = yaml.dump(data, default_flow_style=False, sort_keys=False)
            file_path.write_text(content, encoding="utf-8")
        except Exception as e:
            logger.error(f"Error writing YAML file {file_path}: {str(e)}")


# Global database instance
_database_instance: ResearchDatabase | None = None


def get_research_database() -> ResearchDatabase:
    """Get the global research database instance."""
    global _database_instance
    if _database_instance is None:
        _database_instance = ResearchDatabase()
    return _database_instance
