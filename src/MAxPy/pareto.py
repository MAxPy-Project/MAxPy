import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import csv

def pareto_front(Xs, Ys, maxX = True, maxY = True):
    myList = sorted([[Xs[i], Ys[i], i] for i in range(len(Xs))], reverse=maxX)
    p_front = [myList[0]]
    for pair in myList[1:]:
        if maxY:
            if pair[1] >= p_front[-1][1]:
                p_front.append(pair)
        else:
            if pair[1] <= p_front[-1][1]:
                p_front.append(pair)
    p_frontX = [pair[0] for pair in p_front]
    p_frontY = [pair[1] for pair in p_front]
    p_index = [pair[2] for pair in p_front]
    return p_frontX, p_frontY, p_index












star_size = 200
refsize = 100
fonts = 10

star_exact = "red"
star_ones = "blue"
color_copyA = "gray"
color_copyB = "brown"
color_eta = "yellow"
color_loa = "orange"
color_trunc0 = "purple"
color_trunc1 = "green"

exact = {
    "circuit": [],
    "ssim": [],
    "accuracy": [],
    "area": [],
    "power": [],
    "timing": [],
}

ones = {
    "circuit": [],
    "ssim": [],
    "accuracy": [],
    "area": [],
    "power": [],
    "timing": [],
}

lista_dse = {
    "circuit": [],
    "ssim": [],
    "accuracy": [],
    "area": [],
    "power": [],
    "timing": [],
}

lista_prun = {
    "circuit": [],
    "ssim": [],
    "accuracy": [],
    "area": [],
    "power": [],
    "timing": [],
}

lista_geral = {
    "circuit": [],
    "ssim": [],
    "accuracy": [],
    "area": [],
    "power": [],
    "timing": [],
}

def scatter_separate_circuits(x=[], y=[],  ax=None):

    global star_size
    global fonts

    copyA_x = []
    copyA_y = []
    copyB_x = []
    copyB_y = []
    eta_x = []
    eta_y = []
    loa_x = []
    loa_y = []
    trunc0_x = []
    trunc0_y = []
    trunc1_x = []
    trunc1_y = []

    pcopyA_x = []
    pcopyA_y = []
    pcopyB_x = []
    pcopyB_y = []
    peta_x = []
    peta_y = []
    ploa_x = []
    ploa_y = []
    ptrunc0_x = []
    ptrunc0_y = []
    ptrunc1_x = []
    ptrunc1_y = []

    for i in range(len(lista_geral["circuit"])):
        if "prun" in lista_geral["circuit"][i]:
            if "copyA" in lista_geral["circuit"][i]:
                pcopyA_x.append(x[i])
                pcopyA_y.append(y[i])
            elif "copyB" in lista_geral["circuit"][i]:
                pcopyB_x.append(x[i])
                pcopyB_y.append(y[i])
            elif "eta" in lista_geral["circuit"][i]:
                peta_x.append(x[i])
                peta_y.append(y[i])
            elif "loa" in lista_geral["circuit"][i]:
                ploa_x.append(x[i])
                ploa_y.append(y[i])
            elif "trunc0" in lista_geral["circuit"][i]:
                ptrunc0_x.append(x[i])
                ptrunc0_y.append(y[i])
            elif "trunc1" in lista_geral["circuit"][i]:
                ptrunc1_x.append(x[i])
                ptrunc1_y.append(y[i])
        else:
            if "copyA" in lista_geral["circuit"][i]:
                copyA_x.append(x[i])
                copyA_y.append(y[i])
            elif "copyB" in lista_geral["circuit"][i]:
                copyB_x.append(x[i])
                copyB_y.append(y[i])
            elif "eta" in lista_geral["circuit"][i]:
                eta_x.append(x[i])
                eta_y.append(y[i])
            elif "loa" in lista_geral["circuit"][i]:
                loa_x.append(x[i])
                loa_y.append(y[i])
            elif "trunc0" in lista_geral["circuit"][i]:
                trunc0_x.append(x[i])
                trunc0_y.append(y[i])
            elif "trunc1" in lista_geral["circuit"][i]:
                trunc1_x.append(x[i])
                trunc1_y.append(y[i])

    ax.scatter(copyA_x,     copyA_y,        color=color_copyA,  marker=".", label="_nolegend_")
    ax.scatter(copyB_x,     copyB_y,        color=color_copyB,  marker=".", label="_nolegend_")
    ax.scatter(eta_x,       eta_y,          color=color_eta,    marker=".", label="_nolegend_")
    ax.scatter(loa_x,       loa_y,          color=color_loa,    marker=".", label="_nolegend_")
    ax.scatter(trunc0_x,    trunc0_y,       color=color_trunc0, marker=".", label="_nolegend_")
    ax.scatter(trunc1_x,    trunc1_y,       color=color_trunc1, marker=".", label="_nolegend_")

    ax.scatter(pcopyA_x,     pcopyA_y,     color=color_copyA,   edgecolors="black", marker="o", label="_nolegend_")
    ax.scatter(pcopyB_x,     pcopyB_y,     color=color_copyB,   edgecolors="black", marker="o", label="_nolegend_")
    ax.scatter(peta_x,       peta_y,       color=color_eta,     edgecolors="black", marker="o", label="_nolegend_")
    ax.scatter(ploa_x,       ploa_y,       color=color_loa,     edgecolors="black", marker="o", label="_nolegend_")
    ax.scatter(ptrunc0_x,    ptrunc0_y,    color=color_trunc0, edgecolors="black", marker="o", label="_nolegend_")
    ax.scatter(ptrunc1_x,    ptrunc1_y,    color=color_trunc1,  edgecolors="black", marker="o", label="_nolegend_")


def scatter_pareto(front=[], geral=[], ax=None):

    global star_size
    global fonts
    global ones
    global exact
    flag_acc = False

    copyA_x = []
    copyA_y = []
    copyB_x = []
    copyB_y = []
    eta_x = []
    eta_y = []
    loa_x = []
    loa_y = []
    trunc0_x = []
    trunc0_y = []
    trunc1_x = []
    trunc1_y = []

    for i in range(len(front[0])):
        circ = lista_geral["circuit"][front[2][i]]

        if front[0][i] > 1:
            flag_acc = True

        if "copyA" in circ:
            copyA_x.append(front[0][i])
            copyA_y.append(front[1][i])
        elif "copyB" in circ:
            copyB_x.append(front[0][i])
            copyB_y.append(front[1][i])
        elif "eta" in circ:
            eta_x.append(front[0][i])
            eta_y.append(front[1][i])
        elif "loa" in circ:
            loa_x.append(front[0][i])
            loa_y.append(front[1][i])
        elif "trunc0" in circ:
            trunc0_x.append(front[0][i])
            trunc0_y.append(front[1][i])
        elif "trunc1" in circ:
            trunc1_x.append(front[0][i])
            trunc1_y.append(front[1][i])

    ax.scatter(copyA_x, copyA_y, star_size, color=color_copyA, edgecolors="black", marker="*", label="_nolegend_")
    ax.scatter(copyB_x, copyB_y, star_size, color=color_copyB, edgecolors="black", marker="*", label="_nolegend_")
    ax.scatter(eta_x, eta_y, star_size, color=color_eta, edgecolors="black", marker="*", label="_nolegend_")
    ax.scatter(trunc1_x, trunc1_y, star_size, color=color_trunc1, edgecolors="black", marker="*", label="_nolegend_")
    ax.scatter(trunc0_x, trunc0_y, star_size, color=color_trunc0, edgecolors="black", marker="*", label="_nolegend_")
    ax.scatter(loa_x, loa_y, star_size, color=color_loa, edgecolors="black", marker="*", label="_nolegend_")
    ax.plot(front[0], front[1], color='black', marker='.', linewidth=3, markersize=1, zorder=0)



if __name__ == "__main__":

    area_ref = 180.49
    power_ref = 9.200690000000002
    timing_ref = 187.441864

    min_ssim = 0.85
    min_acc = 0




    with open("sobel_total_pt.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        for row in csv_reader:
            ssim_value = float(float(row[4]))
            accuracy_value = float(row[10])
            area_saving = (1.0 - float(row[2])/area_ref)*100.0
            power_saving = (1.0 - float(row[14])/power_ref)*100.0
            timing_saving = (1.0 - float(row[15])/timing_ref)*100.0
            if "exact" in row[1]:
                exact["circuit"].append(row[1])
                exact["ssim"].append(ssim_value)
                exact["accuracy"].append(accuracy_value)
                exact["area"].append(area_saving)
                exact["power"].append(power_saving)
                exact["timing"].append(timing_saving)
            elif "ones" in row[1]:
                ones["circuit"].append(row[1])
                ones["ssim"].append(ssim_value)
                ones["accuracy"].append(accuracy_value)
                ones["area"].append(area_saving)
                ones["power"].append(power_saving)
                ones["timing"].append(timing_saving)
            #elif ssim_value >= 0.85 and ssim_value < 0.95:
            elif ssim_value >= min_ssim and accuracy_value >= min_acc:
                lista_dse["circuit"].append(row[1])
                lista_dse["ssim"].append(ssim_value)
                lista_dse["accuracy"].append(accuracy_value)
                lista_dse["area"].append(area_saving)
                lista_dse["power"].append(power_saving)
                lista_dse["timing"].append(timing_saving)

    with open("sobel_probprun_pt.csv") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=";")
        for row in csv_reader:
            ssim_value = float(float(row[4]))
            accuracy_value = float(row[10])
            area_saving = (1.0 - float(row[2])/area_ref)*100.0
            power_saving = (1.0 - float(row[14])/power_ref)*100.0
            timing_saving = (1.0 - float(row[15])/timing_ref)*100.0
            #if ssim_value >= 0.85 and ssim_value < 0.95:
            if ssim_value >= min_ssim and accuracy_value >= min_acc:
                lista_prun["circuit"].append(row[1])
                lista_prun["ssim"].append(ssim_value)
                lista_prun["accuracy"].append(accuracy_value)
                lista_prun["area"].append(area_saving)
                lista_prun["power"].append(power_saving)
                lista_prun["timing"].append(timing_saving)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    plt.rcParams["font.family"] = "serif"
    fig, axs = plt.subplots(2, 3)

    lista_geral["circuit"] = lista_dse["circuit"] + lista_prun["circuit"]
    lista_geral["ssim"] = lista_dse["ssim"] + lista_prun["ssim"]
    lista_geral["accuracy"] = lista_dse["accuracy"] + lista_prun["accuracy"]
    lista_geral["area"] = lista_dse["area"] + lista_prun["area"]
    lista_geral["power"] = lista_dse["power"] + lista_prun["power"]
    lista_geral["timing"] = lista_dse["timing"] + lista_prun["timing"]



    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    x = 1
    y = 0
    print("Area saving x Structural Similarity Index Measure")
    front = pareto_frontier(lista_dse["ssim"] + lista_prun["ssim"], lista_dse["area"] + lista_prun["area"])
    plot_front(front, lista_dse["circuit"] + lista_prun["circuit"], lista_dse, lista_prun)
    scatter_separate_circuits(x=lista_geral["ssim"], y=lista_geral["area"], ax=axs[x][y])
    scatter_pareto(front=front, ax=axs[x][y])
    axs[x][y].scatter(exact["ssim"][0], exact["area"][0], refsize, edgecolors='black', color=star_exact, marker="o", label="_nolegend_")
    axs[x][y].scatter(ones["ssim"][0], ones["area"][0], refsize, edgecolors='black', color=star_ones, marker="o", label="_nolegend_")
    axs[x][y].set_xlabel("SSIM", fontsize=fonts)
    axs[x][y].set_ylabel("Circuit Area savings [%]", fontsize=fonts)

    x = 0
    y = 0
    print("Area saving x Accuracy")
    front = pareto_frontier(lista_dse["accuracy"] + lista_prun["accuracy"], lista_dse["area"] + lista_prun["area"])
    plot_front(front, lista_dse["circuit"] + lista_prun["circuit"], lista_dse, lista_prun)
    scatter_separate_circuits(x=lista_geral["accuracy"], y=lista_geral["area"], ax=axs[x][y])
    scatter_pareto(front=front, ax=axs[x][y])
    axs[x][y].scatter(exact["accuracy"][0], exact["area"][0], refsize, edgecolors='black', color=star_exact, marker="o", label="_nolegend_")
    axs[x][y].scatter(ones["accuracy"][0], ones["area"][0], refsize, edgecolors='black', color=star_ones, marker="o", label="_nolegend_")
    axs[x][y].set_xlabel("Edge Detection Accuracy [%]", fontsize=fonts)
    axs[x][y].set_ylabel("Circuit Area savings [%]", fontsize=fonts)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    x = 1
    y = 1
    print("Power saving x Structural Similarity Index Measure")
    front = pareto_frontier(lista_dse["ssim"] + lista_prun["ssim"], lista_dse["power"] + lista_prun["power"])
    plot_front(front, lista_dse["circuit"] + lista_prun["circuit"], lista_dse, lista_prun)
    scatter_separate_circuits(x=lista_geral["ssim"], y=lista_geral["power"], ax=axs[x][y])
    scatter_pareto(front=front, ax=axs[x][y])
    scatter_pareto(front=front, geral=(lista_geral["circuit"] + lista_prun["circuit"]), ax=axs[x][y])
    axs[x][y].scatter(exact["ssim"][0], exact["power"][0], refsize, edgecolors='black', color=star_exact, marker="o", label="_nolegend_")
    axs[x][y].scatter(ones["ssim"][0], ones["power"][0], refsize, edgecolors='black', color=star_ones, marker="o", label="_nolegend_")
    axs[x][y].set_xlabel("SSIM", fontsize=fonts)
    axs[x][y].set_ylabel("Energy savings [%]", fontsize=fonts)

    x = 0
    y = 1
    print("Power saving x Accuracy")
    front = pareto_frontier(lista_dse["accuracy"] + lista_prun["accuracy"], lista_dse["power"] + lista_prun["power"])
    plot_front(front, lista_dse["circuit"] + lista_prun["circuit"], lista_dse, lista_prun)
    scatter_separate_circuits(x=lista_geral["accuracy"], y=lista_geral["power"], ax=axs[x][y])
    scatter_pareto(front=front, ax=axs[x][y])
    axs[x][y].scatter(exact["accuracy"][0], exact["power"][0], refsize, edgecolors='black', color=star_exact, marker="o", label="_nolegend_")
    axs[x][y].scatter(ones["accuracy"][0], ones["power"][0], refsize, edgecolors='black', color=star_ones, marker="o", label="_nolegend_")
    axs[x][y].set_xlabel("Edge Detection Accuracy [%]", fontsize=fonts)
    axs[x][y].set_ylabel("Energy savings [%]", fontsize=fonts)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    x = 1
    y = 2
    print("Timing saving x Structural Similarity Index Measure")
    front = pareto_frontier(lista_dse["ssim"] + lista_prun["ssim"], lista_dse["timing"] + lista_prun["timing"])
    plot_front(front, lista_dse["circuit"] + lista_prun["circuit"], lista_dse, lista_prun)
    scatter_separate_circuits(x=lista_geral["ssim"], y=lista_geral["timing"], ax=axs[x][y])
    scatter_pareto(front=front, ax=axs[x][y])
    axs[x][y].scatter(exact["ssim"][0], exact["timing"][0], refsize, edgecolors='black', color=star_exact, marker="o", label="_nolegend_")
    axs[x][y].scatter(ones["ssim"][0], ones["timing"][0], refsize, edgecolors='black', color=star_ones, marker="o", label="_nolegend_")
    axs[x][y].set_xlabel("Edge Detection Accuracy [%]", fontsize=fonts)
    axs[x][y].set_xlabel("SSIM", fontsize=fonts)
    axs[x][y].set_ylabel("Delay reduction [%]", fontsize=fonts)

    x = 0
    y = 2
    print("Timing saving x Accuracy")
    front = pareto_frontier(lista_dse["accuracy"] + lista_prun["accuracy"], lista_dse["timing"] + lista_prun["timing"])
    plot_front(front, lista_dse["circuit"] + lista_prun["circuit"], lista_dse, lista_prun)
    scatter_separate_circuits(x=lista_geral["accuracy"], y=lista_geral["timing"], ax=axs[x][y])
    scatter_pareto(front=front, ax=axs[x][y])
    axs[x][y].scatter(exact["accuracy"][0], exact["timing"][0], refsize, edgecolors='black', color=star_exact, marker="o", label="Exact 8-bit")
    axs[x][y].scatter(ones["accuracy"][0], ones["timing"][0], refsize, edgecolors='black', color=star_ones, marker="o", label="1's Comp")
    axs[x][y].set_xlabel("Edge Detection Accuracy [%]", fontsize=fonts)
    axs[x][y].set_ylabel("Delay reduction [%]", fontsize=fonts)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    legend_elements = [
        #Line2D([0], [0], color='b', lw=4, label='Line'),
        #Line2D([0], [0], marker='o', color='w', label='Scatter', markerfacecolor='g', markersize=15),
        #Patch(facecolor='orange', edgecolor='r', label='Color Patch')

        Line2D([0], [0], marker='o', color="w", label='Exact 8-bit', markerfacecolor=star_exact, markersize=8),
        Line2D([0], [0], marker='o', color="w", label="1's Comp", markerfacecolor=star_ones, markersize=8),
        Line2D([0], [0], marker='o', color="w", label='Copy A', markerfacecolor=color_copyA, markersize=8),
        Line2D([0], [0], marker='o', color="w", label='Copy B', markerfacecolor=color_copyB, markersize=8),
        Line2D([0], [0], marker='o', color="w", label='ETA-I', markerfacecolor=color_eta, markersize=8),
        Line2D([0], [0], marker='o', color="w", label='LOA', markerfacecolor=color_loa, markersize=8),
        Line2D([0], [0], marker='o', color="w", label='Trunc 0', markerfacecolor=color_trunc0, markersize=8),
        Line2D([0], [0], marker='o', color="w", label='Trunc 1', markerfacecolor=color_trunc1, markersize=8),
        Line2D([0], [0], marker='*', color="w", label='Pareto front', markerfacecolor="black", markersize=15),
    ]

    fig.legend(handles=legend_elements, bbox_to_anchor =(0.5,-0.01), loc='lower center', ncol=11)
    fig.tight_layout(pad=0.3)
    plt.show()

