import unittest


class TestGlobal(unittest.TestCase):

    def test_global_solution(self):
        from dolo import yaml_import, global_solve


        filename = 'examples/global_models/rbc.yaml'

        model = yaml_import(filename)

        import time

        dr = global_solve(model, pert_order=2, maxit=5, smolyak_order=3, verbose=True, polish=True)

        t1 = time.time()


        dr = global_solve(model, pert_order=1, maxit=5, smolyak_order=5, verbose=True, polish=False)

        t2 = time.time()

        dr = global_solve(model, pert_order=1, maxit=5, interp_type='multilinear', verbose=True, polish=False)

        t3 = time.time()

        print(t2-t1)
        print(t3-t2)

if __name__ == '__main__':
    unittest.main()