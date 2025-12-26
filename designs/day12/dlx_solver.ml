(* 
 * Day 12: Dancing Links (DLX) Exact Cover Solver
 * 
 * Implements Knuth's Algorithm X with Dancing Links in hardware.
 * Reference: https://arxiv.org/abs/cs/0011047
 * 
 * Architecture:
 *   Node Memory (BRAM)
 *   Link Traversal Unit
 *   Cover/Uncover FSM
 *   Solution Stack
 * 
 * Node format (64 bits):
 *   [63:54] left link
 *   [53:44] right link
 *   [43:34] up link
 *   [33:24] down link
 *   [23:14] column index
 *   [13:4]  row index
 *   [3:0]   reserved
 * 
 * FSM States:
 *   IDLE, SELECT_COL, COVER, TRY_ROW, RECURSE, UNCOVER, BACKTRACK, DONE
 * 
 * Resources (estimated):
 *   BRAM: Node memory + Column headers + Solution stack
 *   LUTs: ~800 for FSM and link manipulation
 *   Fmax: ~100MHz (BRAM access limited)
 *)

open Hardcaml
open Signal

module DLXNode = struct
  type 'a t = {
    left : 'a [@bits 10];
    right : 'a [@bits 10];
    up : 'a [@bits 10];
    down : 'a [@bits 10];
    column : 'a [@bits 10];
    row : 'a [@bits 10];
  } [@@deriving sexp_of, hardcaml]
end

module DLXColumn = struct
  type 'a t = {
    size : 'a [@bits 10];
    left : 'a [@bits 10];
    right : 'a [@bits 10];
    first : 'a [@bits 10];
    name : 'a [@bits 10];
  } [@@deriving sexp_of, hardcaml]
end

module I = struct
  type 'a t = {
    clock : 'a;
    clear : 'a;
    start : 'a [@bits 1];
    (* Configuration interface for loading matrix *)
    config_valid : 'a [@bits 1];
    config_node : 'a [@bits 64];
    config_addr : 'a [@bits 10];
  } [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t = {
    done_ : 'a [@bits 1];
    solution_valid : 'a [@bits 1];
    solution_row : 'a [@bits 10];
    num_solutions : 'a [@bits 16];
  } [@@deriving sexp_of, hardcaml]
end

(* TODO: Implement create function
 * 
 * Key components to implement:
 * 1. Node BRAM with read/write ports
 * 2. Column header BRAM  
 * 3. Solution stack (BRAM or registers)
 * 4. FSM for Algorithm X control flow
 * 5. Cover/Uncover operation sequencers
 *)

let () = print_endline "Day 12 DLX module structure defined"
