import csv
import pandas as pd
import datetime
from enum import Enum
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from fluids.constants import point
import numpy as np
from prettytable import PrettyTable
from thermo.eos import GCEOS, PR, RK, SRK, VDW

from database.crud import get_compound_by_casid
from database.models import Compound
from db_filler import add_by_id, add_isobaric_points, add_isothermal_points


EOS_STRING = {
    PR: "PR",
    RK: "RK",
    SRK: "SRK",
    VDW: "VDW",
}


def plot_isothermal_for_casid(
    casid: int,
    t: float,
    plow: float,
    phigh: float,
    pstep: float,
    calc_points: int = 1000,
    prop: str = "Density",
):
    # THE MOST GHETTO EQUATION SELECTOR KNOWN TO MAN
    # REMOVE THIS SHT ASAP AND ADD IT TO PARAMETERS
    # SYBAU
    equation_type = RK

    compound = add_by_id(casid)
    Tc, Pc, omega = compound.Tcr, compound.Pcr, compound.accentric
    points = add_isothermal_points(casid, t, plow, phigh, pstep)
    to_plot_exp = []
    to_plot_calc = []
    are = []
    for point in points:
        if prop not in point.properties.keys():
            continue
        to_plot_exp.append((point.P, point.properties[prop]))
        preos = equation_type(
            Tc=Tc, Pc=Pc * 1e6, omega=omega, T=point.T, P=point.P * 1e6
        )
        preos.solve()
        rho_calc = (preos.rho_l if preos.phase == "l" else preos.rho_g) * 1e-3
        rho_exp = point.properties[prop]
        are.append(abs(rho_calc - rho_exp) / rho_exp)
    print(f"MAPE for T = {t}: {100*sum(are) / len(are):.2f}%")
    for p in np.linspace(plow, phigh, calc_points):
        preos = equation_type(Tc=Tc, Pc=Pc * 1e6, omega=omega, T=t, P=p * 1e6)
        preos.solve()
        to_plot_calc.append(
            (p, (preos.rho_l if preos.phase == "l" else preos.rho_g) * 1e-3)
        )
    plt.scatter(
        [i[0] for i in to_plot_exp],
        [i[1] for i in to_plot_exp],
        label=f"Experimental Data",
    )
    plt.plot(
        [i[0] for i in to_plot_calc],
        [i[1] for i in to_plot_calc],
        label=f"Calculated Data",
    )
    plt.title(f"Isothermal data for {compound.name} for T = {t}K")
    plt.xlabel("P, MPa")
    plt.ylabel("ρ, mol/l")
    plt.ylim(20, 32)
    plt.legend()
    plt.show()


def generate_deviation_points(
    compound: Compound,
    point_amount: int,
    t_interval: tuple,
    p_interval: tuple,
    eos: callable,
) -> dict:
    tlow, thigh, tstep = t_interval
    plow, phigh, pstep = p_interval
    result = {}
    for t in np.linspace(tlow, thigh, point_amount):
        current_t = t / compound.Tcr
        result[current_t] = {}
        points = add_isothermal_points(
            t=t, plow=plow, phigh=phigh, pstep=pstep, casid=compound.CasID
        )
        for point in points:
            solver = eos(
                Tc=compound.Tcr,
                Pc=compound.Pcr * 1e6,
                omega=compound.accentric,
                T=point.T,
                P=point.P * 1e6,
            )
            solver.solve()
            rho_calc = (solver.rho_l if solver.phase == "l" else solver.rho_g) * 1e-3
            rho_exp = point.properties["Density"]
            result[current_t][point.P / compound.Pcr] = (
                abs(rho_calc - rho_exp) / rho_exp * 100
            )
    return result


def collect_isothermal_deviations(compound, point_amount, t_interval, p_interval, eos):
    tlow, thigh, tstep = t_interval
    plow, phigh, pstep = p_interval
    result = []
    for t in np.linspace(tlow, thigh, point_amount):
        p_row = []
        points = add_isothermal_points(
            t=t, plow=plow, phigh=phigh, pstep=pstep, casid=compound.CasID
        )
        for point in points:
            solver = eos(
                Tc=compound.Tcr,
                Pc=compound.Pcr * 1e6,
                omega=compound.accentric,
                T=point.T,
                P=point.P * 1e6,
            )
            solver.solve()
            rho_calc = (solver.rho_l if solver.phase == "l" else solver.rho_g) * 1e-3
            rho_exp = point.properties["Density"]
            p_row.append((point.P / compound.Pcr, (abs(rho_calc - rho_exp) / rho_exp)))
        result.append((t / compound.Tcr, tuple(p_row)))
    return result


def collect_isobaric_deviations(compound, point_amount, t_interval, p_interval, eos):
    tlow, thigh, tstep = t_interval
    plow, phigh, pstep = p_interval
    result = []
    for p in np.linspace(plow, phigh, point_amount):
        t_row = []
        points = add_isobaric_points(
            p=p, tlow=tlow, thigh=thigh, tstep=tstep, casid=compound.CasID
        )
        for point in points:
            solver = eos(
                Tc=compound.Tcr,
                Pc=compound.Pcr * 1e6,
                omega=compound.accentric,
                T=point.T,
                P=point.P * 1e6,
            )
            solver.solve()
            rho_calc = (solver.rho_l if solver.phase == "l" else solver.rho_g) * 1e-3
            rho_exp = point.properties["Density"]
            t_row.append((point.T / compound.Tcr, (abs(rho_calc - rho_exp) / rho_exp)))
        result.append((p / compound.Pcr, tuple(t_row)))
    return result


def calculate_deviation_for_casid(
    casid: int,
    calc_interval: tuple,
    point_amount: int,
    eos: callable,
    prop: str = "Density",
):
    result = []
    compound = add_by_id(casid)
    tlow, thigh = calc_interval[0][0] * compound.Tcr, calc_interval[0][1] * compound.Tcr
    plow, phigh = calc_interval[1][0] * compound.Pcr, calc_interval[1][1] * compound.Pcr
    pstep = (phigh - plow) / point_amount
    tstep = (thigh - tlow) / point_amount
    t_interval, p_interval = (tlow, thigh, tstep), (plow, phigh, pstep)
    return generate_deviation_points(
        compound=compound,
        point_amount=point_amount,
        t_interval=t_interval,
        p_interval=p_interval,
        eos=eos,
    )


def plot_data_to_surface(points: dict, graph_name: str = "", method: str = "Unknown"):
    T_list = []
    P_list = []
    Z_list = []

    for T, pressures in points.items():
        for P, deviation in pressures.items():
            T_list.append(T)
            P_list.append(P)
            Z_list.append(deviation)

    # Создаем уникальные значения для сетки
    T_unique = np.array(list(points.keys()))
    P_unique = np.array(list(points[T_unique[0]].keys()))

    T_to_idx = {t: i for i, t in enumerate(T_unique)}
    P_to_idx = {p: i for i, p in enumerate(P_unique)}

    # Создаем матрицу отклонений
    T_grid, P_grid = np.meshgrid(T_unique, P_unique)
    Z_grid = np.full((len(P_unique), len(T_unique)), np.nan)

    T = list(points.keys())
    P = list(points[T[0]].keys())
    extent = [T[0], T[-1], P[0], P[-1]]
    for T, pressures in points.items():
        for P, deviation in pressures.items():
            i = P_to_idx[P]
            j = T_to_idx[T]
            Z_grid[i, j] = deviation

    '''fig, ax = plt.subplots()
    cax = ax.imshow(
        Z_grid,
        origin="lower",
        aspect="auto",
        cmap="gray",
        vmin=0,
        vmax=5,
        extent=extent,
    )'''
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(
        T_grid,
        P_grid,
        Z_grid,
        cmap='gray')

    font_params = {"fontname": "Times New Roman"}
    ax.set_xlabel("Tr", **font_params)
    ax.set_ylabel("Pr", **font_params)
    ax.set_zlabel("MAPE", **font_params)
    ax.zaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_zlim(0, 5)
    ax.set_box_aspect(None, zoom=0.85)
    plt.colorbar(surf, ax=ax, location="left")
    if graph_name == "":
        now = datetime.datetime.now()
        graph_name = f"unknown-Graph-{now:%d-%m-%Y-%H-%M-%S}.png"
    plt.savefig(graph_name, dpi=300, bbox_inches="tight")


def plot_data_to_imshow(points: dict, graph_name: str = "", method: str = "Unknown"):
    T_list = []
    P_list = []
    Z_list = []

    for T, pressures in points.items():
        for P, deviation in pressures.items():
            T_list.append(T)
            P_list.append(P)
            Z_list.append(deviation)

    # Создаем уникальные значения для сетки
    T_unique = np.array(list(points.keys()))
    P_unique = np.array(list(points[T_unique[0]].keys()))

    T_to_idx = {t: i for i, t in enumerate(T_unique)}
    P_to_idx = {p: i for i, p in enumerate(P_unique)}

    # Создаем матрицу отклонений
    T_grid, P_grid = np.meshgrid(T_unique, P_unique)
    Z_grid = np.full((len(P_unique), len(T_unique)), np.nan)

    T = list(points.keys())
    P = list(points[T[0]].keys())
    extent = [T[0], T[-1], P[0], P[-1]]
    for T, pressures in points.items():
        for P, deviation in pressures.items():
            i = P_to_idx[P]
            j = T_to_idx[T]
            Z_grid[i, j] = deviation

    fig, ax = plt.subplots()
    cax = ax.imshow(
        Z_grid,
        origin="lower",
        aspect="auto",
        extent=extent,
    )

    font_params = {"fontname": "Times New Roman"}
    ax.set_xlabel("Tr", **font_params)
    ax.set_ylabel("Pr", **font_params)
    cbar = plt.colorbar(cax, ax=ax, location="right")
    cbar.set_label("MAPE, %")
    if graph_name == "":
        now = datetime.datetime.now()
        graph_name = f"unknown-Graph-{now:%d-%m-%Y-%H-%M-%S}.png"
    plt.savefig(graph_name, dpi=300, bbox_inches="tight")


def write_point_into_csv(points: dict, log_name: str = "") -> bool:
    if log_name == "":
        now = datetime.datetime.now()
        log_name = f"unknown-Report-{now:%d-%m-%Y-%H-%M-%S}.csv"
    keys = list(points.keys())
    with open(log_name, "w", newline="") as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=";")
        top_row = ["\t"] + [round(i, 2) for i in points[keys[0]]]
        spamwriter.writerow(top_row)
        for key in keys:
            spamwriter.writerow(
                [round(key, 2)]
                + [str(round(points[key][i], 2)) + "%" for i in points[key]]
            )
    return True


def print_average_mape(
    mape: dict,
    compound: str = "Unknown compound",
    eos: str = "Unknown method",
    interval: str = "Unknown"
):
    result = 0
    count = 0
    for T in mape:
        row = mape[T]
        for P in row:
            result += row[P]
            count += 1
    result /= count
    print(f"Average MAPE for {compound} on interval {interval} using {eos} = {result:.2f}%")


if __name__ == "__main__":
    # plot_isothermal_for_casid(124389, 275, 60, 80, 1)
    # True - isothermic, False - isobaric
    # (t, p)
    quarters = {"l": ((1.1, 1.25), (1.1, 1.25)), "g": ((1.1, 1.25), (0.75, 0.9))}
    casids = [124389, 74828, 7727379, 7732185, 630080, 7446095]
    for casid in casids:
        compound = add_by_id(casid)

        quarter = "g"
        for eos in EOS_STRING:
            mape = calculate_deviation_for_casid(
                casid=casid,
                point_amount=10,
                eos=eos,
                calc_interval=quarters[quarter],
            )
            now = datetime.datetime.now()
            log_name = f"{compound.name}-{quarter}-Report-{EOS_STRING[eos]}-{now:%d-%m-%Y-%H-%M-%S}.csv"
            graph_name = f"{compound.name}-{quarter}-Graph-{EOS_STRING[eos]}-{now:%d-%m-%Y-%H-%M-%S}.png"
            print_average_mape(mape=mape,
                               compound=compound.name,
                               eos=EOS_STRING[eos],
                               interval=quarter)
            plot_data_to_imshow(mape, graph_name=graph_name, method=EOS_STRING[eos])
            write_point_into_csv(mape, log_name=log_name)
