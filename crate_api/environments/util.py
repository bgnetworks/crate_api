# query and manipulate labgrid configuration environments.
import sys


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('please supply a path to an environment yaml as the sole argument.')
        exit(1)
    
    from crate_api import Environment

    import pathlib
    
    env = Environment(str(pathlib.Path(sys.argv[1]).resolve()))
    main = env.get_target()

    def print_class_name(l):
        for c in l:
            # list of parent classes that are in the 'protocol' submodule, kinda hacky, won't work on classes another layer deep
            pl = [(v.__name__) for v in c.__class__.__bases__ if v.__module__.split('.')[-2] == 'protocol'] 
            print(type(c).__name__, f"name:'{c.name}'" if c.name is not None else '', f'protocols:{pl}' if len(pl) > 0 else "")

    print('# Resources:')
    print_class_name(main.resources)
    print('# Drivers:')
    print_class_name(main.drivers)
