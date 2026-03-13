"""
visualizer.py — Interactive Concept Visualizations
Embeds PhET, GeoGebra, VisuAlgo, and more
"""
import streamlit as st

VISUALIZERS = {
    "⚡ Physics": [
        {"name": "Energy Skate Park",        "url": "https://phet.colorado.edu/sims/html/energy-skate-park-basics/latest/energy-skate-park-basics_en.html", "desc": "Explore conservation of energy"},
        {"name": "Wave Interference",         "url": "https://phet.colorado.edu/sims/html/wave-interference/latest/wave-interference_en.html",               "desc": "Visualize wave patterns"},
        {"name": "Projectile Motion",         "url": "https://phet.colorado.edu/sims/html/projectile-motion/latest/projectile-motion_en.html",               "desc": "Study projectile trajectories"},
        {"name": "Electric Field",            "url": "https://phet.colorado.edu/sims/html/charges-and-fields/latest/charges-and-fields_en.html",             "desc": "Visualize electric fields"},
        {"name": "Circuit Construction",      "url": "https://phet.colorado.edu/sims/html/circuit-construction-kit-dc/latest/circuit-construction-kit-dc_en.html", "desc": "Build and test circuits"},
    ],
    "🧪 Chemistry": [
        {"name": "Molecule Shapes",           "url": "https://phet.colorado.edu/sims/html/molecule-shapes/latest/molecule-shapes_en.html",                   "desc": "3D molecular geometry"},
        {"name": "Atomic Interactions",       "url": "https://phet.colorado.edu/sims/html/atomic-interactions/latest/atomic-interactions_en.html",           "desc": "Explore atom bonding"},
        {"name": "Acid-Base Solutions",       "url": "https://phet.colorado.edu/sims/html/acid-base-solutions/latest/acid-base-solutions_en.html",           "desc": "pH and acid-base chemistry"},
        {"name": "Balancing Chemical Eqns",   "url": "https://phet.colorado.edu/sims/html/balancing-chemical-equations/latest/balancing-chemical-equations_en.html", "desc": "Balance chemical equations"},
    ],
    "📐 Mathematics": [
        {"name": "GeoGebra Graphing",         "url": "https://www.geogebra.org/graphing",                                                                    "desc": "Plot and analyze functions"},
        {"name": "GeoGebra Geometry",         "url": "https://www.geogebra.org/geometry",                                                                    "desc": "Interactive geometry builder"},
        {"name": "GeoGebra 3D Calculator",    "url": "https://www.geogebra.org/3d",                                                                          "desc": "3D graphs and surfaces"},
        {"name": "GeoGebra Classic",          "url": "https://www.geogebra.org/classic",                                                                     "desc": "Full math toolkit"},
        {"name": "Fraction Matcher",          "url": "https://phet.colorado.edu/sims/html/fraction-matcher/latest/fraction-matcher_en.html",                 "desc": "Visual fraction comparison"},
    ],
    "💻 Algorithms": [
        {"name": "Sorting Algorithms",        "url": "https://visualgo.net/en/sorting",                                                                      "desc": "Bubble, merge, quick sort"},
        {"name": "Binary Search Tree",        "url": "https://visualgo.net/en/bst",                                                                          "desc": "BST insert, delete, search"},
        {"name": "Graph Algorithms",          "url": "https://visualgo.net/en/graphds",                                                                      "desc": "BFS, DFS traversal"},
        {"name": "Linked List",               "url": "https://visualgo.net/en/list",                                                                         "desc": "Linked list operations"},
        {"name": "Heap",                      "url": "https://visualgo.net/en/heap",                                                                         "desc": "Min/max heap operations"},
    ],
    "🧬 Biology": [
        {"name": "Natural Selection",         "url": "https://phet.colorado.edu/sims/html/natural-selection/latest/natural-selection_en.html",               "desc": "Evolution simulation"},
        {"name": "Gene Expression",           "url": "https://phet.colorado.edu/sims/html/gene-expression-essentials/latest/gene-expression-essentials_en.html", "desc": "DNA to protein"},
        {"name": "Membrane Channels",         "url": "https://phet.colorado.edu/sims/html/membrane-channels/latest/membrane-channels_en.html",               "desc": "Cell membrane transport"},
    ],
}


def visualizer_page():
    st.markdown("""
    <div style='margin-bottom:1.5rem;'>
        <h1 style='font-size:26px; font-weight:700; color:#1a1a2e; margin:0;'>🔬 Concept Visualizer</h1>
        <p style='color:#888; font-size:13px; margin:4px 0 0;'>Interactive simulations to understand concepts visually</p>
    </div>
    """, unsafe_allow_html=True)

    col_sub, col_sim = st.columns([1, 3])

    with col_sub:
        st.markdown("**Select Subject**")
        subject = st.radio("", list(VISUALIZERS.keys()), label_visibility="collapsed")

    with col_sim:
        sims = VISUALIZERS[subject]
        st.markdown(f"**{subject} Simulations**")

        sim_names = [s["name"] for s in sims]
        selected_name = st.selectbox("Choose simulation", sim_names, label_visibility="collapsed")
        selected = next(s for s in sims if s["name"] == selected_name)

        st.markdown(f"""
        <div style='background:#f8f9fa; border:1px solid #e0e0e0; border-radius:12px;
             padding:12px 16px; margin-bottom:12px; display:flex; align-items:center; gap:12px;'>
            <div>
                <div style='font-weight:600; font-size:14px;'>{selected['name']}</div>
                <div style='color:#888; font-size:12px;'>{selected['desc']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.components.v1.iframe(selected["url"], height=520, scrolling=True)

        st.caption("💡 Use your mouse to interact with the simulation directly.")

    st.markdown("---")
    st.markdown("**All Available Simulations**")
    for subj, sims in VISUALIZERS.items():
        with st.expander(subj):
            cols = st.columns(2)
            for i, sim in enumerate(sims):
                with cols[i % 2]:
                    st.markdown(f"**{sim['name']}**")
                    st.caption(sim['desc'])
