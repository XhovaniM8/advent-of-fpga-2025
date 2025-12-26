(*
 * Day 10: GF(2) Gaussian Elimination Solver
 *
 * Solves systems of linear equations over GF(2) (binary field).
 * All arithmetic is XOR-based with no carry chains.
 *
 * Architecture:
 *   Matrix BRAM -> Row Selector -> XOR Array -> Write Back
 *
 * Operations:
 *   - Row XOR: Parallel XOR of entire row (single cycle)
 *   - Pivot Find: Priority encoder on column
 *   - Row Swap: BRAM address remapping
 *
 * FSM States:
 *   IDLE -> FIND_PIVOT -> SWAP_ROWS -> ELIMINATE -> NEXT_COL -> BACK_SUB -> DONE
 *
 * Parameters:
 *   MATRIX_SIZE: Number of variables (default 64 for 8x8 grid)
 *   ROW_WIDTH: Bits per row including augmented column
 *
 * Resources (estimated for 64x65 matrix):
 *   BRAM: ~4KB (matrix storage)
 *   LUTs: ~400 (XOR array + control)
 *   Fmax: ~300MHz (pure combinational XOR)
 *)

open Hardcaml
open Signal

module Config = struct
  let matrix_size = 64  (* 8x8 lights out grid *)
  let row_width = 65    (* matrix_size + 1 for augmented column *)
end

module I = struct
  type 'a t = {
    clock : 'a;
    clear : 'a;
    (* Matrix loading interface *)
    load_valid : 'a [@bits 1];
    load_row : 'a [@bits 6];
    load_data : 'a [@bits 65];
    (* Control *)
    start : 'a [@bits 1];
  } [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t = {
    done_ : 'a [@bits 1];
    solution_valid : 'a [@bits 1];
    solution_data : 'a [@bits 64];
    no_solution : 'a [@bits 1];
  } [@@deriving sexp_of, hardcaml]
end

(* TODO: Implement create function
 *
 * Key components:
 * 1. Matrix BRAM (matrix_size rows x row_width bits)
 * 2. Current column register
 * 3. Pivot row register
 * 4. XOR unit (row_width parallel XOR gates)
 * 5. Priority encoder for pivot finding
 * 6. FSM controller
 *)

let () = print_endline "Day 10 GF(2) solver module defined"
