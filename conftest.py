# ce fichierf est importé par playwright et la fonction qui est définie dedans permet d'accepter la présence des options
# mais on parse quand même ces options "manuellement" car je n'ai pas compris comment utiliser les "meta options"
def pytest_addoption(parser):
    parser.addoption("--entree"   , action="store", default=None)
    parser.addoption("--rapport"  , action="store", default=None)
    parser.addoption("--config"   , action="store", default=None)
    parser.addoption("--execution", action="store_true", default=None)

# def pytest_generate_tests(metafunc):
#     # This is called for every test. Only get/set command line arguments
#     # if the argument is specified in the list of test "fixturenames".
#     option_value = metafunc.config.option.input
#     if 'input' in metafunc.fixturenames and option_value is not None:
#         metafunc.parametrize("input", [option_value])
