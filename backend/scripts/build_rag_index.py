from app.services.rag import BiomedicalRAGService


if __name__ == "__main__":
    service = BiomedicalRAGService()
    print(f"RAG index ready using backend: {service.backend_name}")
    print(f"Indexed {len(service.docs)} documents.")
