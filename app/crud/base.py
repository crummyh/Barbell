from typing import Protocol, TypeVar, runtime_checkable, Any
from sqlmodel import Session

# Type variables
ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType') 
UpdateSchemaType = TypeVar('UpdateSchemaType')

@runtime_checkable
class CRUDModuleProtocol(Protocol, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Protocol for modules containing CRUD functions.
    
    This allows your existing function-based modules to be type-checked
    against a common interface without refactoring to classes.
    """
    
    def create(self, session: Session, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record."""
        ...
    
    def get(self, session: Session, id: int) -> ModelType | None:
        """Get a record by ID."""
        ...
    
    def update(
        self, 
        session: Session, 
        id: int, 
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType | None:
        """Update a record by ID."""
        ...
    
    def delete(self, session: Session, id: int) -> bool:
        """Delete a record by ID."""
        ...
