def sum_function(*args: tuple, error_data: dict = None):
    if error_data is None:
        error_data = {
            'error_path': [0],
            'errors': [],
            'deep_index': 0
        }

    all_sum = 0
    is_num_only = all(isinstance(arg, (int, float)) for arg in args)

    if is_num_only:
        return sum(args)

    for index, arg in enumerate(args):
        error_data['error_path'][error_data['deep_index']] = index

        if isinstance(arg, str):
            error_string = ''.join([f'[{i}]' for i in error_data['error_path']])
            error_data['errors'].append(error_string)

        elif isinstance(arg, (list, tuple)):
            error_data['deep_index']  += 1
            error_data['error_path'].append(0)
            arg = sum_function(*arg, error_data=error_data)


        if isinstance(arg, list):
            error_data['deep_index'] -= 1
            error_data['error_path'].pop()

        if isinstance(arg, int):
            all_sum += arg

    if error_data['errors']:
        all_sum = error_data['errors']
    return all_sum


def get_results(*args):
    print(f'{args} ===> {sum_function(*args)}', end="\n ========= \n")


list_of_args = (
    (1, 2, 3),
    (1, [3, 5], 4),
    (1, [3, ([1, 5], 1)], 4),
    (1, [3, ([1, 'dfgh', 9 , 'sd'], 1, 'asa')], 4), # error => [1][1][0][1], [1][1][2]
)

for args in list_of_args:
    get_results(*args)



def my_generator(from_number: int, to_number: int):
    while from_number <= to_number:
        yield from_number
        from_number += 1

for i in my_generator(0, 10):
    print(i)


class MyIterator():
    def __init__(self, current: int|str|float = None, end: int|str|float = None) -> int|str|float:
        self.current = current
        self.end = end

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.end:
            raise StopIteration
        self.current += 1
        return self.current - 1

for i in MyIterator(12, 20):
    print(i)
