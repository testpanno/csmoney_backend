from pydantic import BaseModel

class DomainCreate(BaseModel):
    domain_name: str

class DomainUpdate(BaseModel):
    domain_name: str

class DomainResponse(BaseModel):
    id: int
    domain_name: str

    class Config:
        from_attributes = True