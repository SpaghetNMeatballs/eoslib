import matplotlib.pyplot as plt
from db_filler import add_by_id, add_isothermal_points
from thermo.eos import PR
from numpy import linspace


def plot_isothermal_for_casid(
        casid: int, t: float, plow: float, phigh: float, pstep: float, calc_points: int = 1000
):
    prop = "Density"
    compound = add_by_id(casid)
    Tc, Pc, omega = compound.Tcr, compound.Pcr, compound.accentric
    points = add_isothermal_points(casid, t, plow, phigh, pstep)
    to_plot_exp = []
    to_plot_calc = []
    for point in points:
        if prop not in point.properties.keys():
            continue
        to_plot_exp.append((point.P, point.properties[prop]))
    for p in linspace(plow, phigh, calc_points):
        preos = PR(Tc, Pc * 1e6, omega, t, p * 1e6)
        preos.solve()
        to_plot_calc.append((p, (preos.rho_l if preos.phase is "l" else preos.rho_g) * 1e-3))
    plt.scatter([i[0] for i in to_plot_exp], [i[1] for i in to_plot_exp], label=f"Experimental Data")
    plt.plot([i[0] for i in to_plot_calc], [i[1] for i in to_plot_calc],
             label=f"Calculated Data", )
    plt.title(f"Isothermal data for {compound.name} for T = {t}K")
    plt.xlabel("P, MPa")
    plt.ylabel("ρ, mol/l")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    plot_isothermal_for_casid(124389, 300, 60, 80, 1)
