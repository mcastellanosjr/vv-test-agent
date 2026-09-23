from pydantic import BaseModel, Field

from models.requirement import Requirement


class ImportFinding(BaseModel):
    row_number: int | None = None
    requirement_id: str | None = None
    field: str | None = None
    message: str


class ImportedRequirement(BaseModel):
    project: str
    requirement: Requirement


class RequirementImportResult(BaseModel):
    source_file: str

    imported_requirements: list[
        ImportedRequirement
    ] = Field(default_factory=list)

    errors: list[
        ImportFinding
    ] = Field(default_factory=list)

    warnings: list[
        ImportFinding
    ] = Field(default_factory=list)

    total_rows: int = 0
    requirement_count: int = 0
    acceptance_criteria_count: int = 0

    @property
    def valid(self) -> bool:
        return not self.errors