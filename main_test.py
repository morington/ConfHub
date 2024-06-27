import dataclasses

from confhub import Confhub


if __name__ == '__main__':
    data: type[dataclasses.dataclass] = Confhub(developer_mode=False).data

    print(data.postgresql.scheme)
