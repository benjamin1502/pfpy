# File: cluster.py
# Author: Claudio David Lopez

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from matplotlib import pyplot as plt
from scipy.cluster.hierarchy import dendrogram

from pfsim import PowerFactorySim


FOLDER_NAME = ''
PROJECT_NAME = '2A4G'
STUDY_CASE_NAME = 'Study Case'


def plot_dendrogram(model, **kwargs):
    # Children of hierarchical clustering
    children = model.children_
    # Distances between each pair of children
    # Since we don't have this information,
    #we can use a uniform one for plotting
    distance = np.arange(1, children.shape[0]+1)
    # The number of observations contained in each cluster level
    no_of_observations = np.arange(2, children.shape[0]+2)
    # Create linkage matrix and then plot the dendrogram
    linkage_matrix = np.column_stack(
        [children, distance, no_of_observations]).astype(float)
    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)


if __name__ == '__main__':
    # activate project and study case
    sim = PowerFactorySim(
        folder_name=FOLDER_NAME,
        project_name=PROJECT_NAME,
        study_case_name=STUDY_CASE_NAME)
    # get elements that connect terminals (lines
    # and trafos) into a list
    lines = sim.app.GetCalcRelevantObjects('*.ElmLne')
    trafos = sim.app.GetCalcRelevantObjects('*.ElmTr2')
    links = lines + trafos
    # load results from file
    voltages = pd.DataFrame.from_csv(
        'res_prob_lf.csv', sep=',', index_col=None)
    bus_names = voltages.columns.values
    # create zero-filled DataFrame with the structure
    # of the adjacency matrix
    adjacency = pd.DataFrame(
        0, index=bus_names, columns=bus_names)
    # fill in the adjacency matrix with 1s where a connection exists
    for link in links:
        # get terminals at each extreme of the line or transformer
        from_bus = link.GetNode(0)[0].loc_name
        to_bus = link.GetNode(1)[0].loc_name
        # set corresponding elements in adjacency matrix to 1
        adjacency.set_value(from_bus, to_bus, 1)
        adjacency.set_value(to_bus, from_bus, 1)
    # create an agglomerative clustering object
    ac = AgglomerativeClustering(
        n_clusters=5,
        connectivity=adjacency.values)
    # cluster the results
    model = ac.fit(np.transpose(voltages.values))
    dendrogram_labels = []
    for bus, label in zip(bus_names, ac.labels_):
        dendrogram_labels.append(
            #str(bus)+'\nCluster '+ str(label))
            str(bus))
        print(bus, label)

    # plot cluster dendrogram
    plot_dendrogram(model, labels=dendrogram_labels, 
        color_threshold=0, orientation='right')
    plt.subplots_adjust(left=0.15)
    frame = plt.gca()
    frame.axes.get_xaxis().set_visible(False)
    plt.show()
