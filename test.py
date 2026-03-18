from eo_tides.utils import list_models

available_models, valid_models = list_models(
    directory='tide_models'
)

print("Available models:", available_models)
print("Valid models:", valid_models)