"""Unit tests for research database service."""

import shutil
import tempfile

import pytest
import yaml

from src.services.research_database import ResearchDatabase


class TestResearchDatabase:
    """Test suite for ResearchDatabase class."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary research database for testing."""
        temp_dir = tempfile.mkdtemp()
        db = ResearchDatabase(base_path=temp_dir)
        yield db
        # Cleanup
        shutil.rmtree(temp_dir)

    def test_create_session_directory(self, temp_db):
        """Test creating session directory structure."""
        session_id = "test-session-123"
        ticker = "AAPL"

        session_dir = temp_db.create_session_directory(session_id, ticker)

        # Verify directory structure
        assert session_dir.exists()
        assert session_dir.name == ticker

        # Check agent subdirectories
        agent_dirs = ["valuation", "strategic", "historical", "synthesis", "meta"]
        for agent_dir in agent_dirs:
            assert (session_dir / agent_dir).exists()

        # Check metadata files
        meta_dir = session_dir / "meta"
        assert (meta_dir / "file_index.yaml").exists()
        assert (meta_dir / "cross_references.yaml").exists()
        assert (meta_dir / "agent_activity.yaml").exists()

    def test_metadata_file_initialization(self, temp_db):
        """Test that metadata files are properly initialized."""
        session_id = "test-session-123"
        ticker = "AAPL"

        session_dir = temp_db.create_session_directory(session_id, ticker)
        meta_dir = session_dir / "meta"

        # Check file index
        file_index_path = meta_dir / "file_index.yaml"
        with open(file_index_path) as f:
            file_index = yaml.safe_load(f)

        assert file_index["session_id"] == session_id
        assert file_index["ticker"] == ticker
        assert "created_at" in file_index
        assert file_index["files"] == {}

        # Check cross references
        cross_refs_path = meta_dir / "cross_references.yaml"
        with open(cross_refs_path) as f:
            cross_refs = yaml.safe_load(f)

        assert cross_refs["session_id"] == session_id
        assert cross_refs["ticker"] == ticker
        assert cross_refs["references"] == []

        # Check agent activity
        activity_path = meta_dir / "agent_activity.yaml"
        with open(activity_path) as f:
            activity = yaml.safe_load(f)

        assert activity["session_id"] == session_id
        assert activity["ticker"] == ticker
        assert "agents" in activity
        assert "valuation_agent" in activity["agents"]

    def test_write_research_file(self, temp_db):
        """Test writing a research file with metadata."""
        session_id = "test-session-123"
        ticker = "AAPL"
        agent_type = "valuation"
        filename = "dcf_analysis_v1.md"
        content = "# DCF Analysis for Apple Inc.\n\nDetailed financial analysis..."

        # Create session directory first
        temp_db.create_session_directory(session_id, ticker)

        # Write research file
        file_path = temp_db.write_research_file(
            session_id=session_id,
            ticker=ticker,
            agent_type=agent_type,
            filename=filename,
            content=content,
            metadata={"priority": "high", "complexity": "advanced"}
        )

        assert file_path.exists()

        # Read file content
        file_content = file_path.read_text(encoding="utf-8")

        # Should have YAML header
        assert file_content.startswith("---\n")
        assert content in file_content

        # Parse YAML header
        parts = file_content.split("---\n")
        yaml_content = parts[1]
        metadata = yaml.safe_load(yaml_content)

        assert metadata["session_id"] == session_id
        assert metadata["ticker"] == ticker
        assert metadata["agent_type"] == agent_type
        assert metadata["priority"] == "high"
        assert metadata["complexity"] == "advanced"

    def test_read_research_file(self, temp_db):
        """Test reading a research file with metadata parsing."""
        session_id = "test-session-123"
        ticker = "AAPL"
        agent_type = "valuation"
        filename = "test_analysis.md"
        content = "# Test Analysis\n\nTest content for analysis."

        # Create session and write file
        temp_db.create_session_directory(session_id, ticker)
        temp_db.write_research_file(session_id, ticker, agent_type, filename, content)

        # Read file back
        relative_path = f"{agent_type}/{filename}"
        file_data = temp_db.read_research_file(session_id, ticker, relative_path)

        assert "metadata" in file_data
        assert "content" in file_data
        assert file_data["content"] == content
        assert file_data["metadata"]["session_id"] == session_id
        assert file_data["metadata"]["ticker"] == ticker
        assert file_data["metadata"]["agent_type"] == agent_type

    def test_read_nonexistent_file(self, temp_db):
        """Test reading a file that doesn't exist."""
        session_id = "test-session-123"
        ticker = "AAPL"

        with pytest.raises(FileNotFoundError):
            temp_db.read_research_file(session_id, ticker, "nonexistent/file.md")

    def test_get_session_files(self, temp_db):
        """Test getting all files for a session."""
        session_id = "test-session-123"
        ticker = "AAPL"

        # Create session and write multiple files
        temp_db.create_session_directory(session_id, ticker)

        files_to_create = [
            ("valuation", "dcf_analysis.md", "DCF analysis content"),
            ("strategic", "competitive_analysis.md", "Competitive analysis content"),
            ("historical", "company_history.md", "Company history content")
        ]

        for agent_type, filename, content in files_to_create:
            temp_db.write_research_file(session_id, ticker, agent_type, filename, content)

        # Get all session files
        files = temp_db.get_session_files(session_id, ticker)

        assert len(files) == 3

        # Check file information
        for file_info in files:
            assert "path" in file_info
            assert "metadata" in file_info
            assert "size" in file_info
            assert "created_at" in file_info
            assert file_info["metadata"]["session_id"] == session_id

    def test_get_agent_context_first_agent(self, temp_db):
        """Test getting context for first agent (no dependencies)."""
        session_id = "test-session-123"
        ticker = "AAPL"

        temp_db.create_session_directory(session_id, ticker)

        # First agent should get empty context
        context = temp_db.get_agent_context(session_id, ticker, "valuation")

        assert context["session_id"] == session_id
        assert context["ticker"] == ticker
        assert context["requesting_agent"] == "valuation"
        assert context["previous_research"] == {}

    def test_get_agent_context_with_dependencies(self, temp_db):
        """Test getting context for agent with dependencies."""
        session_id = "test-session-123"
        ticker = "AAPL"

        # Create session and add valuation research
        temp_db.create_session_directory(session_id, ticker)
        temp_db.write_research_file(
            session_id, ticker, "valuation", "dcf_analysis.md",
            "# DCF Analysis\n\nDetailed valuation analysis."
        )

        # Strategic agent should get valuation context
        context = temp_db.get_agent_context(session_id, ticker, "strategic")

        assert context["session_id"] == session_id
        assert context["ticker"] == ticker
        assert context["requesting_agent"] == "strategic"
        assert "valuation" in context["previous_research"]
        assert len(context["previous_research"]["valuation"]) == 1

    def test_add_cross_reference(self, temp_db):
        """Test adding cross-references between files."""
        session_id = "test-session-123"
        ticker = "AAPL"

        temp_db.create_session_directory(session_id, ticker)

        # Add cross-reference
        temp_db.add_cross_reference(
            session_id, ticker,
            "valuation/dcf_analysis.md",
            "strategic/competitive_moat.md",
            "DCF analysis references competitive advantages"
        )

        # Check cross-references were saved
        cross_refs = temp_db._read_cross_references(session_id, ticker)

        assert len(cross_refs["references"]) == 1
        ref = cross_refs["references"][0]
        assert ref["source"] == "valuation/dcf_analysis.md"
        assert ref["target"] == "strategic/competitive_moat.md"
        assert ref["relationship"] == "DCF analysis references competitive advantages"
        assert "created_at" in ref

    def test_file_index_updates(self, temp_db):
        """Test that file index is updated when files are written."""
        session_id = "test-session-123"
        ticker = "AAPL"

        temp_db.create_session_directory(session_id, ticker)

        # Write a file
        temp_db.write_research_file(
            session_id, ticker, "valuation", "test_file.md", "Test content"
        )

        # Check file index was updated
        file_index = temp_db._read_file_index(session_id, ticker)

        # Use os.path.join or check for both path separators to be OS-agnostic
        expected_key = "valuation/test_file.md"
        windows_key = "valuation\\test_file.md"
        assert expected_key in file_index["files"] or windows_key in file_index["files"]
        # Get the actual key that exists
        actual_key = next(key for key in file_index["files"].keys() if "test_file.md" in key)
        file_info = file_index["files"][actual_key]
        assert "created_at" in file_info
        assert "updated_at" in file_info

    def test_agent_activity_updates(self, temp_db):
        """Test that agent activity is updated when files are written."""
        session_id = "test-session-123"
        ticker = "AAPL"

        temp_db.create_session_directory(session_id, ticker)

        # Write a file
        temp_db.write_research_file(
            session_id, ticker, "valuation", "analysis.md", "Analysis content"
        )

        # Check agent activity was updated
        activity = temp_db._read_agent_activity(session_id, ticker)

        assert activity["agents"]["valuation_agent"]["status"] == "active"
        assert len(activity["agents"]["valuation_agent"]["files"]) == 1
        file_info = activity["agents"]["valuation_agent"]["files"][0]
        assert file_info["filename"] == "analysis.md"
        assert "created_at" in file_info

    def test_yaml_file_operations(self, temp_db):
        """Test YAML file reading and writing operations."""
        test_file = temp_db.base_path / "test.yaml"
        test_data = {
            "session_id": "test-123",
            "ticker": "AAPL",
            "data": {
                "key1": "value1",
                "key2": ["item1", "item2"]
            }
        }

        # Write YAML file
        temp_db._write_yaml_file(test_file, test_data)
        assert test_file.exists()

        # Read YAML file
        read_data = temp_db._read_yaml_file(test_file)
        assert read_data == test_data

    def test_yaml_file_error_handling(self, temp_db):
        """Test YAML file error handling."""
        nonexistent_file = temp_db.base_path / "nonexistent.yaml"

        # Reading nonexistent file should return None
        result = temp_db._read_yaml_file(nonexistent_file)
        assert result is None

    def test_agent_dependency_mapping(self, temp_db):
        """Test agent dependency mapping for context retrieval."""
        session_id = "test-session-123"
        ticker = "AAPL"

        temp_db.create_session_directory(session_id, ticker)

        # Create files for all agent types
        agents_and_files = [
            ("valuation", "dcf.md", "DCF content"),
            ("strategic", "competition.md", "Competition content"),
            ("historical", "timeline.md", "Timeline content")
        ]

        for agent_type, filename, content in agents_and_files:
            temp_db.write_research_file(session_id, ticker, agent_type, filename, content)

        # Test synthesis agent context (should have access to all previous)
        context = temp_db.get_agent_context(session_id, ticker, "synthesis")

        assert "valuation" in context["previous_research"]
        assert "strategic" in context["previous_research"]
        assert "historical" in context["previous_research"]

        # Test strategic agent context (should have access to valuation only)
        context = temp_db.get_agent_context(session_id, ticker, "strategic")

        assert "valuation" in context["previous_research"]
        assert "strategic" not in context["previous_research"]
        assert "historical" not in context["previous_research"]
