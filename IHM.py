import sys
import random
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import networkx as nx

# ---------------------------------------------------------------------------
#  Helpers ------------------------------------------------------------------
# ---------------------------------------------------------------------------

try:
    from networkx.drawing.nx_pydot import graphviz_layout

    def _gv_layout(graph):
        """Try different ways to get a left‑to‑right dot layout."""
        try:
            return graphviz_layout(graph, prog="dot", args="-Grankdir=LR")
        except TypeError:
            g2 = graph.copy()
            g2.graph["graph"] = {"rankdir": "LR"}
            return graphviz_layout(g2, prog="dot")

    HAS_GRAPHVIZ = True
except Exception:
    HAS_GRAPHVIZ = False


def horizontal_layout(graph):
    if HAS_GRAPHVIZ:
        try:
            return _gv_layout(graph)
        except Exception:
            pass
    pos = nx.spring_layout(graph, k=2.0, seed=42)
    for n, (x, y) in pos.items():
        pos[n] = (x * 3, y)
    return pos


# ---------------------------------------------------------------------------
#  Load user data -----------------------------------------------------------
# ---------------------------------------------------------------------------

automates = {
    "bloquer": {
        "DETECTER_POSITION_ADVERSAIRE": {
            "action": "Localiser joueur",
            "transitions": {
                "POSITION_TROUVEE": "CALCULER_POSITION_BLOCAGE",
                "ECHEC_VISION": "ECHEC"
            },
            "I": True,
            "F": False
        },
        "CALCULER_POSITION_BLOCAGE": {
            "action": "Calculer où se placer pour bloquer",
            "transitions": {
                "POSITION_OK": "SE_DEPLACER_POSITION",
                "CALCUL_IMPOSSIBLE": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "SE_DEPLACER_POSITION": {
            "action": "Aller à la position de blocage",
            "transitions": {
                "POSITION_ATTEINTE": "AJUSTER_POSITION_SUIVANT_ADVERSAIRE",
                "ERREUR_DEPLACEMENT": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "AJUSTER_POSITION_SUIVANT_ADVERSAIRE": {
            "action": "S'ajuster si joueur bouge",
            "transitions": {
                "POSITION_STABLE": "MAINTENIR_POSITION",
                "JOUEUR_PERDU": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "MAINTENIR_POSITION": {
            "action": "Maintenir la position de blocage",
            "transitions": {
                "JOUEUR_BLOQUE": "MISSION_OK",
                "POSITION_PERDUE": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "MISSION_OK": {
            "action": "Mission accomplie : joueur bloqué",
            "transitions": {},
            "I": False,
            "F": True
        },
        "ECHEC": {
            "action": "Mission échouée",
            "transitions": {},
            "I": False,
            "F": True
        }
    },
    "se placer entre la balle et le but": {
        "DETECTER_POSITION_BALLE":{
            "action": "localiser balle",
            "transitions": {
                "POSITION_TROUVEE": "CALCULER_POSITION_BLOCAGE",
                "ECHEC_VISION": "ECHEC"
            },
            "I": True,
            "F": False
        },
        "CALCULER_POSITION_BLOCAGE":{
            "action": "Calculer où se placer pour bloquer",
            "transitions": {
                "POSITION_OK": "SE_DEPLACER_POSITION",
                "CALCUL_IMPOSSIBLE": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "SE_DEPLACER_POSITION": {
            "action": "Aller à la position de blocage",
            "transitions": {
                "POSITION_ATTEINTE": "AJUSTER_POSITION_SUIVANT_BALLE",
                "ERREUR_DEPLACEMENT": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "AJUSTER_POSITION_SUIVANT_BALLE": {
            "action": "S'ajuster si balle bouge",
            "transitions": {
                "POSITION_STABLE": "MAINTENIR_POSITION",
                "JOUEUR_PERDU": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "MAINTENIR_POSITION": {
            "action": "Maintenir la position de blocage",
            "transitions": {
                "JOUEUR_BLOQUE": "MISSION_OK",
                "POSITION_PERDUE": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "MISSION_OK": {
            "action": "Mission accomplie : joueur bloqué",
            "transitions": {},
            "I": False,
            "F": True
        },
        "ECHEC": {
            "action": "Mission échouée",
            "transitions": {},
            "I": False,
            "F": True
        }    
    },
    "intercepter une passe": {                                                  
        "DETECTER_PASSE_ADVERSE": {
            "action": "Localiser passe adverse",
            "transitions": {
                "POSITION_TROUVEE": "ANTICIPER_TRAJECTOIRE_PASSE",
                "ECHEC_VISION": "ECHEC"
            },
            "I": True,
            "F": False
        },
        "ANTICIPER_TRAJECTOIRE_PASSE": {
            "action": "Calculer où se placer pour intercepter",
            "transitions": {
                "POSITION_OK": "SE_DEPLACER_POSITION",
                "CALCUL_IMPOSSIBLE": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "SE_DEPLACER_POSITION": {
            "action": "Aller à la position de blocage",
            "transitions": {
                "POSITION_ATTEINTE": "INTERCEPTER_BALLE",
                "ERREUR_DEPLACEMENT": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "INTERCEPTER_BALLE": {
            "action": "Intercepter la balle",
            "transitions": {
                "POSITION_ATTEINTE": "DÉGAGER_BALLE",
                "ERREUR_DEPLACEMENT": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "DÉGAGER_BALLE": {
            "action": "Dégager la balle",
            "transitions": {
                "DEGAGEMENT REUSSI": "MISSION_OK",
                "ECHEC DEGAGEMENT": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "MISSION_OK": {
                "action": "Mission accomplie : joueur bloqué",
                "transitions": {},
                "I": False,
                "F": True
        },
        "ECHEC": {
            "action": "Mission échouée",
            "transitions": {},
            "I": False,
            "F": True
        } 
    },
    "marquer un joueur": {
        "DETECTER_POSITION_ADVERSAIRE": {
            "action": "Localiser joueur",
            "transitions": {
                "POSITION_TROUVEE": "SUIVRE_JOUEUR",
                "ECHEC_VISION": "ECHEC"
            },
            "I": True,
            "F": False
        },
        "SUIVRE_JOUEUR": {
            "action": "Suivre le joueur",
            "transitions": {
                "JOUEUR_SUIVI": "MAINTENIR_POSITION",
                "ECHEC_SUIVI": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "MAINTENIR_POSITION": {
            "action": "Maintenir la position de blocage",
            "transitions": {
                "JOUEUR_BLOQUE": "MISSION_OK",
                "POSITION_PERDUE": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "MISSION_OK": {
            "action": "Mission accomplie : joueur bloqué",
            "transitions": {},
            "I": False,
            "F": True
        },
        "ECHEC": {
            "action": "Mission échouée",
            "transitions": {},
            "I": False,
            "F": True
        }     
    },
    "protéger le but": {
        "SE_POSITIONNER_ZONE": {
            "action": "Se positionner dans la zone de réparation",
            "transitions": {
                "POSITION_ADEQUATE": "SURVEILLER_BALLE",
                "ECHEC_POSITION": "ECHEC"
            },
            "I": True,
            "F": False
        },
        "SURVEILLER_BALLE": {
            "action": "Surveiller la balle",
            "transitions": {
                "TIR_ADVERSE": "BLOQUER_TIR",
                "ECHEC_POSITION": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "BLOQUER_TIR": {
            "action": "Bloquer le tir adverse",
            "transitions": {
                "TIR_ADVERSE": "MISSION_OK",
                "PAS_DE_TIR": "ECHEC"
            },
            "I": False,
            "F": False
        },
        "MISSION_OK": {
            "action": "Mission accomplie : joueur bloqué",
            "transitions": {},
            "I": False,
            "F": True
        },
        "ECHEC": {
            "action": "Mission échouée",
            "transitions": {},
            "I": False,
            "F": True
        }       
    }
}


# ---------------------------------------------------------------------------
#  Matplotlib canvas --------------------------------------------------------
# ---------------------------------------------------------------------------

class GraphCanvas(FigureCanvas):
    """Matplotlib canvas able to draw *one* selected automate."""

    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots(figsize=(14, 4))
        super().__init__(self.fig)
        self.ax.axis("off")

    def draw_automate(self, states: dict, current: str, visited: set[str], final_states: set[str]):
        """Redraw the graph for *states* description."""
        G = nx.MultiDiGraph()
        for src, info in states.items():
            for label, dst in info["transitions"].items():
                G.add_edge(src, dst, label=label)

        pos = horizontal_layout(G)

        # Node colors ------------------------------------------------------
        node_colors = []
        for n in G.nodes():
            if n == current:
                node_colors.append("red")
            elif n in final_states:
                node_colors.append("lightgreen")
            elif n in visited:
                node_colors.append("skyblue")
            else:
                node_colors.append("lightgray")

        # Edge labels ------------------------------------------------------
        edge_labels = {
            (u, v): ", ".join(sorted({d["label"] for d in G.get_edge_data(u, v).values()}))
            for u, v in G.edges()
        }

        self.ax.clear()
        self.ax.axis("off")
        nx.draw_networkx_nodes(
            G,
            pos,
            ax=self.ax,
            node_color=node_colors,
            node_size=900,
            edgecolors="black",
        )
        # Label with the *action* description just under the state name -----
        full_labels = {n: f"{n}\n{states[n]['action']}" for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=full_labels, ax=self.ax, font_size=7)
        nx.draw_networkx_edges(
            G,
            pos,
            ax=self.ax,
            connectionstyle="arc3,rad=0.1",
            arrows=True,
            arrowstyle="-|>",
        )
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=self.ax, font_size=7)
        self.fig.tight_layout()
        self.draw()


# ---------------------------------------------------------------------------
#  Main window --------------------------------------------------------------
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulateur d’automates défenseurs")
        self.resize(1500, 750)

        # --- Widgets ------------------------------------------------------
        self.task_combo = QComboBox()
        self.task_combo.addItems(list(automates.keys()))

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Aléatoire", "Manuel"])

        self.start_button = QPushButton("Démarrer la simulation")
        self.start_button.clicked.connect(self.start_simulation)

        self.transition_list = QListWidget()
        self.transition_list.itemClicked.connect(self.on_transition_click)
        self.transition_list.setEnabled(False)

        # Left panel -------------------------------------------------------
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Sélection de la tâche :"))
        left_layout.addWidget(self.task_combo)
        left_layout.addSpacing(5)
        left_layout.addWidget(QLabel("Mode de choix de l’événement :"))
        left_layout.addWidget(self.mode_combo)
        left_layout.addWidget(self.start_button)
        left_layout.addSpacing(10)
        left_layout.addWidget(QLabel("Événements possibles :"))
        left_layout.addWidget(self.transition_list)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        # Graph panel ------------------------------------------------------
        self.graph_canvas = GraphCanvas()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.graph_canvas)
        splitter.setStretchFactor(1, 1)

        central = QWidget()
        central.setLayout(QHBoxLayout())
        central.layout().addWidget(splitter)
        self.setCentralWidget(central)

        # Simulation state -------------------------------------------------
        self.states = {}  # Will hold the automate for the *selected* task
        self.current_state: str | None = None
        self.final_states: set[str] = set()
        self.visited: set[str] = set()

        # Draw an empty placeholder
        self.graph_canvas.draw_automate({}, "", set(), set())

    # ---------------------------------------------------------------------
    #  Simulation logic ----------------------------------------------------
    # ---------------------------------------------------------------------

    def _init_from_task(self, task: str):
        """Extract states, initial, final for *task*."""
        self.states = automates[task]
        self.current_state = next(s for s, info in self.states.items() if info.get("I"))
        self.final_states = {s for s, info in self.states.items() if info.get("F")}
        self.visited = {self.current_state}

    def start_simulation(self):
        # Prepare ----------------------------------------------------------
        task = self.task_combo.currentText()
        self._init_from_task(task)
        self.transition_list.clear()

        # Draw initial graph ----------------------------------------------
        self.graph_canvas.draw_automate(self.states, self.current_state, self.visited, self.final_states)

        # First step -------------------------------------------------------
        transitions = self.states[self.current_state]["transitions"]
        if not transitions:
            self.statusBar().showMessage("Pas de transitions depuis l’état initial !")
            return

        if self.mode_combo.currentText() == "Aléatoire":
            first_event = random.choice(list(transitions.keys()))
            self.apply_event(first_event)
            self.transition_list.setEnabled(True)
        else:
            # Manual – let the user pick
            self.populate_transition_list(sorted(transitions))
            self.transition_list.setEnabled(True)

    # ------------------------------------------------------------------
    #  UI helpers -------------------------------------------------------
    # ------------------------------------------------------------------

    def populate_transition_list(self, events: list[str]):
        self.transition_list.clear()
        for ev in events:
            item = QListWidgetItem(ev)
            item.setData(Qt.UserRole, ev)
            self.transition_list.addItem(item)

    def on_transition_click(self, item: QListWidgetItem):
        ev = item.data(Qt.UserRole)
        self.apply_event(ev)

    # ------------------------------------------------------------------
    #  Core transition --------------------------------------------------
    # ------------------------------------------------------------------

    def apply_event(self, event: str):
        transitions = self.states[self.current_state]["transitions"]
        if event not in transitions:
            self.statusBar().showMessage("Transition impossible depuis l’état courant !", 5000)
            return

        self.current_state = transitions[event]
        self.visited.add(self.current_state)
        self.graph_canvas.draw_automate(self.states, self.current_state, self.visited, self.final_states)

        next_trans = self.states[self.current_state]["transitions"]
        if not next_trans:
            self.transition_list.setEnabled(False)
            if self.current_state in self.final_states:
                self.statusBar().showMessage("🔵 Simulation terminée : état final atteint !")
            else:
                self.statusBar().showMessage("🔴 Simulation bloquée : aucun successeur.")
        else:
            if self.mode_combo.currentText() == "Aléatoire":
                self.populate_transition_list(sorted(next_trans))
            else:
                self.populate_transition_list(sorted(next_trans))


# ---------------------------------------------------------------------------
#  Run ----------------------------------------------------------------------
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
