Architecture overview
=====================

.. graphviz::
    :name: sphinx.ext.graphviz
    :caption: Architecture overview
    :alt: How the module is organized
    :align: center

     digraph "sphinx-ext-graphviz" {
        size="6,4";
        rankdir="LR";
        graph [fontname="Verdana", fontsize="12"];
        node [fontname="Verdana", fontsize="12"];
        edge [fontname="Sans", fontsize="9"];

        NodeWindowEditor [label="NodeEditorWindow", shape="folder",];
        nodes [label="Nodes (list of Node)"];
        edges [label="Edges (list of Edge)"];
        Inputs [label="Inputs (list of Socket)"];
        Outputs [label="Outputs (list of Socket)"];

        NodeWindowEditor -> NodeEditorWidget [label=" holds "];
        NodeEditorWidget -> Scene [label=" holds "];
        NodeEditorWidget -> grScene [label=" holds "];
        Scene -> nodes;
        Scene -> edges;

        Node -> grNode;
        Node -> Content;
        Node -> Inputs;
        Node -> Outputs;
     }
