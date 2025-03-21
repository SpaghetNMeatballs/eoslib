from thermo.eos import GCEOS
import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from csv_experimental_loader import load_csv

R = 8.3144621


class VanDerWaalsEOS(GCEOS):
    def __init__(self, Tc, Pc):
        a = (27 * (R * Tc) ** 2) / (64 * Pc)
        b = (R * Tc) / (8 * Pc)
        super().__init__()
        self.a = a
        self.b = b
        self.Tc = Tc
        self.Pc = Pc

    def Z(self, T, P):
        a, b = self.a, self.b
        A = a * P / (R**2 * T**2)
        B = b * P / (R * T)
        coefficients = [1, -(1 + B), A, -A * B]
        roots = np.roots(coefficients)
        roots = np.real(roots[np.isreal(roots)])

        return self._select_root(roots, T, P)

    def _select_root(self, roots, T, P):
        if T > self.Tc:
            return np.max(roots)
        elif P > self.Pc:
            return np.min(roots)
        else:
            return np.max(roots)

    def rho(self, T, P):
        Z = self.Z(T, P)
        return P / (Z * R * T)


class RedlichKwongEOS(GCEOS):
    def __init__(self, Tc, Pc):
        a = 0.42748 * (R**2) * (Tc**2.5) / Pc
        b = 0.08664 * R * Tc / Pc
        super().__init__()
        self.a = a
        self.b = b
        self.Tc = Tc
        self.Pc = Pc

    def Z(self, T, P):
        a, b = self.a, self.b
        A = a * P / (R**2 * T**2)
        B = b * P / (R * T)
        coefficients = [1, -(1 + B), A, -A * B]
        roots = np.roots(coefficients)
        roots = np.real(roots[np.isreal(roots)])

        return self._select_root(roots, T, P)

    def _select_root(self, roots, T, P):
        if T > self.Tc:
            return np.max(roots)
        elif P > self.Pc:
            return np.min(roots)
        else:
            return np.max(roots)

    def rho(self, T, P):
        Z = self.Z(T, P)
        return P / (Z * R * T)


class TrebbleBishnoiEOS(GCEOS):
    def __init__(self, Tc, Pc, omega):
        k = 0.37464 + 1.54226 * omega - 0.26992 * omega**2
        a = 0.45724 * (R**2) * Tc**2 / Pc
        b = 0.07780 * R * Tc / Pc
        super().__init__()
        self.a = a
        self.b = b
        self.k = k
        self.Tc = Tc
        self.Pc = Pc
        self.omega = omega

    def alpha(self, T):
        Tr = T / self.Tc
        return (1 + self.k * (1 - Tr**0.5)) ** 2

    def Z(self, T, P):
        a, b, alpha = self.a, self.b, self.alpha(T)
        A = a * alpha * P / (R**2 * T**2)
        B = b * P / (R * T)
        coefficients = [1, -(1 + B), A, -A * B]
        roots = np.roots(coefficients)
        roots = np.real(roots[np.isreal(roots)])

        return self._select_root(roots, T, P)

    def _select_root(self, roots, T, P):
        if T > self.Tc:
            return np.max(roots)
        elif P > self.Pc:
            return np.min(roots)
        else:
            return np.max(roots)

    def rho(self, T, P):
        Z = self.Z(T, P)
        return P / (Z * R * T)


def plots():
    # Критические параметры для метана
    Tc = 190.56  # К
    Pc = 4599000  # Па
    omega = 0.011  # Фактор асимметрии

    vdW = VanDerWaalsEOS(Tc, Pc)
    RK = RedlichKwongEOS(Tc, Pc)
    TB = TrebbleBishnoiEOS(Tc, Pc, omega)

    # Температура и давление
    T = 300  # K
    P = 1e5  # Па

    t_field = np.arange(140, 241, 20)
    p_field = np.arange(1, 7, 0.1)
    fig, ax = plt.subplots(2, 3)
    ax = ax.flatten()

    experimental_data_vapor = load_csv("methane_experimental.csv", "vapor")
    experimental_data_liquid = load_csv("methane_experimental.csv", "liquid")
    experimental_data_supercrit = load_csv("methane_experimental.csv", "supercritical")

    # Расчёт отклонений
    phase_dict = {
        "vapor": experimental_data_vapor,
        "liquid": experimental_data_liquid,
        "supercritical": experimental_data_supercrit,
    }
    for phase in phase_dict.keys():
        print(f"{phase.title():-^35}")
        vdw = []
        rk = []
        tb = []
        for point in phase_dict[phase]:
            t, p, rho_exp = point
            rho_vdw = vdW.rho(t, p)
            rho_rk = RK.rho(t, p)
            rho_tb = TB.rho(t, p)
            vdw_delta = abs((rho_exp - rho_vdw) / rho_exp) * 100
            rk_delta = abs((rho_exp - rho_rk) / rho_exp) * 100
            tb_delta = abs((rho_exp - rho_tb) / rho_exp) * 100

            vdw.append(vdw_delta)
            rk.append(rk_delta)
            tb.append(tb_delta)

            print(f"are_vdw({t:.0f},{p:.0f}): {vdw_delta:.2f}%")
            print(f"are_rk({t:.0f},{p:.0f}): {rk_delta:.2f}%")
            print(f"are_tb({t:.0f},{p:.0f}): {tb_delta:.2f}%")
        print(f"avg(vdw) = {sum(vdw) / len(vdw):.2f}")
        print(f"avg(rk) = {sum(rk) / len(rk):.2f}")
        print(f"avg(tb) = {sum(tb) / len(tb):.2f}")

    # Построение графиков
    for i in range(len(t_field)):
        t = t_field[i]
        rho_calc_vdw = []
        rho_calc_rk = []
        rho_calc_tb = []
        for p in p_field:
            rho_calc_vdw.append(vdW.rho(t, p))
            rho_calc_rk.append(RK.rho(t, p))
            rho_calc_tb.append(TB.rho(t, p))
        plt.plot(p_field, rho_calc_vdw, label="Van Der Waals")
        plt.plot(p_field, rho_calc_rk, label="Redlich Kwong")
        plt.plot(p_field, rho_calc_tb, label="Trebble Bishnoi")
        exp_points_vapor = []
        exp_points_liquid = []
        exp_points_supercrit = []
        for point in experimental_data_vapor:
            if point[0] == t and p_field[0] <= point[1] <= p_field[-1]:
                exp_points_vapor.append((point[1], point[2]))
        for point in experimental_data_liquid:
            if point[0] == t and p_field[0] <= point[1] <= p_field[-1]:
                exp_points_liquid.append((point[1], point[2]))
        for point in experimental_data_supercrit:
            if point[0] == t and p_field[0] <= point[1] <= p_field[-1]:
                exp_points_supercrit.append((point[1], point[2]))
        plt.scatter(
            [j[0] for j in exp_points_vapor],
            [j[1] for j in exp_points_vapor],
            label=f"Experimental Data in vapor phase",
        )
        plt.scatter(
            [j[0] for j in exp_points_liquid],
            [j[1] for j in exp_points_liquid],
            label=f"Experimental Data in liquid phase",
        )
        plt.scatter(
            [j[0] for j in exp_points_supercrit],
            [j[1] for j in exp_points_supercrit],
            label=f"Experimental Data in supercrit phase",
        )
        plt.title(f"T = {t} K")
        plt.xlabel("P, MPa")
        plt.ylabel("ρ, mol/m3")
        plt.show()


# Пример использования:
if __name__ == "__main__":
    plots()
