import matplotlib.pyplot as plt
import numpy as np
import itertools
from collections import defaultdict
import json


def nested_dict(): return defaultdict(nested_dict)


BAR_WIDTH = 0.25


def plot(operation, ops):
    tasks = ops[operation]
    with plt.xkcd():
        fig, axes = plt.subplots(figsize=(10, 20))
        for i, (name, contenders) in enumerate(tasks.items()):
            axes = plt.subplot(len(tasks), 1, i+1)
            axes.set_title(f"{operation} {name} [operations/second]")
            N = len(contenders)
            indices = np.arange(N)  # the x locations for the groups
            axes.set_xticks(indices)
            axes.set_xticklabels(contenders.keys())

            for i, (name, ops) in enumerate(contenders.items()):
                color = "#0809fe" if name == "hyperjson" else "#fe4ed8"
                axes.bar(i, ops, BAR_WIDTH, color=color)

        plt.tight_layout()
        plt.savefig(f'assets/{operation}.png')


def get_ops():
    data = nested_dict()
    with open("benchmark.json") as f:
        raw = json.load(f)
        for benchmark in raw["benchmarks"]:
            name, test = benchmark["param"].split('-', 1)
            ops = benchmark["stats"]["ops"]
            group = benchmark["group"]
            data[group][test][name] = ops
    return data


if __name__ == "__main__":
    ops = get_ops()
    plot("serialize", ops)
    plot("deserialize", ops)
