import matplotlib.pyplot as plt
from fluids.constants import point

from database.models import Compound
from db_filler import add_by_id, add_isothermal_points, add_isobaric_points
from thermo.eos import PR, RK, VDW, GCEOS, SRK
from numpy import linspace


from prettytable import PrettyTable


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
    for p in linspace(plow, phigh, calc_points):
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
    for t in linspace(tlow, thigh, point_amount):
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
    for t in linspace(tlow, thigh, point_amount):
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
    for p in linspace(plow, phigh, point_amount):
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


# mode = False - compress rows, True - invert then compress rows
def process_mape(mape, mode: bool = True, prop: str = "T"):
    print(f"{prop}\t|MAPE")
    for row in mape:
        row_mape = sum([i[1] for i in row[1]]) / len(row[1]) * 100
        print(f"{row[0]:.2f}|{row_mape:.2f}%".replace(".", ","))


def write_point_into_csv(point: dict) -> bool:

    return True


if __name__ == "__main__":
    # plot_isothermal_for_casid(124389, 275, 60, 80, 1)
    # True - isothermic, False - isobaric
    mode = True
    mape = calculate_deviation_for_casid(
        casid=124389,
        point_amount=10,
        eos=SRK,
        calc_interval=((0.75, 1), (0.75, 1)),
    )
    pass
