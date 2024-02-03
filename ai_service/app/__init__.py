from main import main
import asyncio
from modules.initialize_models_utility.initialize_models import InitializeModels

if __name__ == "__main__":
    initialize_models: InitializeModels = InitializeModels()
    initialize_models.initialize_models()
    asyncio.run(main())