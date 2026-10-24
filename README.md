♟️ Chess Engine — From Scratch in Python

«Building a chess engine from the ground up, one move at a time.»

A personal chess engine project focused on understanding the mechanics behind chess software, from board representation and legal move generation to search algorithms, position evaluation, and eventually a playable web interface.

The goal is not simply to connect an existing engine and build a chessboard around it. The goal is to understand how the pieces fit together and build as much of the engine as possible from scratch.

🚧 Current Status

Phase 1 — Chessboard and Core Logic

The project is currently in its early development stage. The foundation is a Python-based chessboard with an explicit representation of the pieces and empty squares.

Implemented so far

- [x] Python chessboard class
- [x] Constants for white and black chess pieces
- [x] Explicit piece representation using strings, such as "wK", "bQ", and "wP"
- [x] Empty-square representation
- [x] Text-based board display
- [x] Complete legal move generation
- [x] Check, checkmate, and stalemate detection
- [ ] Special moves and draw rules
- [ ] Chess engine search and position evaluation
- [x] Playable graphical interface
- [ ] Web deployment

The checklist tracks development milestones; only completed features should be marked as implemented.

🧩 Project Philosophy

This project prioritizes learning, experimentation, and understanding over taking shortcuts.

- Build from scratch: Implement the core mechanics instead of relying on a ready-made chess engine.
- Understand the fundamentals: Develop a strong foundation in board representation, move generation, search, and evaluation.
- Experiment with ideas: Explore different algorithms and potentially novel approaches to chess engine design.
- Keep improving: Test, benchmark, debug, and refine each component as the project evolves.
- Make it accessible: Eventually bring the engine to a website so people can interact with it through a graphical chessboard.

🛠️ Planned Architecture

The engine is intended to evolve through several independent components.

Component| Responsibility
Board representation| Store pieces, colors, and square occupancy
Move generation| Generate candidate moves for each piece
Move legality| Reject moves that violate chess rules
Game state| Track turns, castling rights, en passant, and other state
Search| Explore possible move sequences
Evaluation| Estimate the strength of a position
Engine interface| Connect the engine to a graphical board
Web interface| Allow users to play against the engine in a browser

These components will be developed incrementally as the project progresses.

🗺️ Roadmap

Phase 1 — The Board

- [x] Define piece constants and the empty-square representation
- [x] Create the initial board representation
- [x] Display the board in the terminal
- [x] Implement reliable piece movement
- [x] Handle captures and pawn movement
- [x] Validate moves against the rules of chess

Phase 2 — A Complete Chess Rules System

- [x] Implement king-safety checks
- [x] Detect check, checkmate, and stalemate
- [x] Implement castling and en passant
- [x] Implement pawn promotion
- [ ] Track draw conditions
- [x] Test positions and edge cases

Phase 3 — The Engine

- [ ] Implement a baseline search algorithm
- [ ] Add a position evaluation function
- [ ] Introduce alpha-beta pruning and move ordering
- [ ] Benchmark playing strength and search performance
- [ ] Explore transposition tables and iterative deepening
- [ ] Experiment with more advanced evaluation methods

Phase 4 — Testing and Research

- [ ] Validate move generation against established chess test positions
- [ ] Run tactical and endgame tests
- [ ] Measure search speed and playing strength
- [ ] Compare design choices using repeatable experiments
- [ ] Investigate advanced techniques, including neural-network-based evaluation, where practical

Phase 5 — A Playable Chess Website

- [ ] Connect the Python engine to a graphical chessboard
- [ ] Implement communication between the interface and engine
- [ ] Make the application accessible through a website
- [ ] Deploy the project online

The roadmap is experimental and may change as new ideas are tested.

💻 Development Environment

The project is being developed in Python on an Android phone, using a mobile Python development environment and Git tooling.

The initial focus is on getting the underlying chess logic right before investing time in graphics or web development.

🎯 Long-Term Vision

The long-term ambition is to build a highly competitive chess engine and investigate how far a from-scratch implementation can go.

A potential future goal is to compete with established engines such as Stockfish. That is an ambitious research objective, not a claim about the current strength or capabilities of this project.

The immediate priority is simple: build a correct foundation, test it rigorously, and improve it one component at a time.

📌 Project Status

Early development — board representation and foundational logic.

This is an evolving personal project. Features, architecture, and performance will change as development continues.

---

Built with Python, curiosity, and a lot of chess. ♟️