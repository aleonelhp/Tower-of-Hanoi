# Tower of Hanoi - Interactive Automaton

A visual and interactive implementation of the classic Tower of Hanoi problem modeled as a finite automaton, with JFLAP export and manual practice mode.

## Features

- **Automatic Generation**: Creates the complete automaton for n disks (1-10)
- **Animated Visualization**: Watch the optimal solution step-by-step with smooth animations
- **Manual Mode**: Practice solving the problem yourself with real-time feedback
- **State Diagram**: Live visualization of the automaton and your progress
- **Export Options**:
  - CSV for data analysis
  - JFLAP (.jff) for academic use
- **Playback Controls**: Play, Pause, Next, Previous with adjustable speed

## Installation

### Requirements
- Python 3.7+
- tkinter (included in most Python installations)

### Running
```bash
python TowerOfHanoi.py
or
ToerOfHanoi.exe
```

No external dependencies required - it's a single file!

## Usage

### Automatic Mode
1. Select the number of disks (1-10)
2. Click "Generate Automaton"
3. Use playback controls:
   - **Play**: Run through the complete solution
   - **Next/Prev**: Step forward or backward
   - **Speed**: Adjust animation speed

### Manual Mode
1. Generate an automaton first
2. Click "Manual Mode"
3. Solve the problem:
   - Click on a peg to select a disk
   - Click on the destination peg to move
4. The system validates each move automatically
5. Visualize your path compared to the optimal solution

### Export

#### CSV
- Saves all automaton states
- Format: `index, pegA, pegB, pegC`
- Useful for data analysis and processing

#### JFLAP
- Exports as JFLAP-compatible .jff file
- Perfect for academic use and automaton visualization
- Includes labeled states and transitions

## Academic Context

This project models the Tower of Hanoi as a **deterministic finite automaton** where:
- Each **state** represents a disk configuration
- Each **transition** represents a valid move (A→B, A→C, B→C, etc.)
- The **initial state** has all disks on peg A
- The **final state** has all disks on peg C

### Complexity
For n disks:
- **Total states**: 2^n (one per step + initial)
- **Moves**: 2^n - 1
- **Runtime**: O(2^n)

## Interface
```
┌─────────────────────────────────────────────────────┐
│  Controls: Generate | Export | Play/Pause          │
├──────────────────────┬──────────────────────────────┤
│                      │  Automaton Diagram           │
│   Animated           │  ┌─────────────────────────┐ │
│   Visualization      │  │ q0→q1→q2→...→qn        │ │
│   of 3 Pegs          │  └─────────────────────────┘ │
│                      │                              │
│      A    B    C     │  Move Log                    │
│      │    │    │     │  ┌─────────────────────────┐ │
│     ═╧═   │    │     │  │ A→C                    │ │
│    ══╧══  │    │     │  │ A→B                    │ │
│   ═══╧═══ │    │     │  │ ...                    │ │
│  ════╧════ │    │     │  └─────────────────────────┘ │
└──────────────────────┴──────────────────────────────┘
```

## Key Features

- **Real-time Validation**: Manual mode prevents illegal moves
- **Visual Feedback**: Smooth animations and clear error messages
- **Goal Indicator**: In manual mode, peg C is clearly marked as the target
- **Solution Comparison**: Upon completion, compare your solution with the optimal one
- **Clean Architecture**: Modular and well-documented code

## Code Structure
```python
AutomataHanoiMatricial  # Automaton logic
├── _build()            # Generates states and transitions
├── export_csv()        # Exports to CSV
├── export_jflap()      # Exports to JFLAP
└── simulate_manual()   # Simulates move sequence

HanoiGUI                # Graphical interface
├── generar()           # Creates the automaton
├── animate_move()      # Smooth animations
├── toggle_manual()     # Interactive mode
└── draw_automaton_diagram()  # Automaton visualization
```

## Educational Applications

Ideal for:
- **Automata Theory** courses
- Teaching **Recursion** and **Divide and Conquer**
- **Data Structures** labs
- Demonstrating **Exponential Complexity**
- **JFLAP** practice

## Technical Highlights

- **State Space Representation**: Each configuration is stored as immutable tuples
- **Recursive Solution Generation**: Classic divide-and-conquer implementation
- **Event-driven Animation**: Smooth disk movements using tkinter's after() scheduler
- **JFLAP XML Export**: Properly formatted for academic tools
- **Interactive Validation**: Real-time move legality checking

## License

This project is available under the MIT License. Feel free to use it for educational and academic purposes.

## Known Issues

- Character encoding in Spanish labels (legacy issue)
- Maximum: 10 disks
