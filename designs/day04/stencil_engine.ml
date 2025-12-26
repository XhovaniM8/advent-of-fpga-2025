(*
 * Day 4: Parameterized Stencil Engine for Pattern Matching
 *
 * Architecture:
 *   Input Stream -> Line Buffers -> Sliding Window -> Pattern Matchers -> Match Counter
 *
 * Line Buffer: BRAM storing (window_height - 1) rows
 * Sliding Window: Register array extracting NxN region
 * Pattern Matchers: Parallel comparators for all 8 directions
 *
 * Parameters:
 *   GRID_WIDTH: Input grid width (default 140)
 *   WINDOW_SIZE: Sliding window dimension (default 7 for 4-char pattern)
 *   PATTERN_LEN: Pattern length (default 4 for "XMAS")
 *
 * Resources (estimated for 140x140 grid, 7x7 window):
 *   BRAM: ~7KB (line buffers)
 *   LUTs: ~300 (comparators + control)
 *   Registers: ~400 (sliding window)
 *   Fmax: ~250MHz
 *)

open Hardcaml
open Signal

module Config = struct
  let grid_width = 140
  let window_size = 7
  let pattern_len = 4
  let char_bits = 8
end

module I = struct
  type 'a t = {
    clock : 'a;
    clear : 'a;
    (* Streaming input *)
    char_valid : 'a [@bits 1];
    char_data : 'a [@bits 8];
    row_end : 'a [@bits 1];
    (* Control *)
    start : 'a [@bits 1];
  } [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t = {
    done_ : 'a [@bits 1];
    match_count : 'a [@bits 16];
    ready : 'a [@bits 1];
  } [@@deriving sexp_of, hardcaml]
end

(* TODO: Implement create function
 *
 * Key components:
 * 1. Line buffer BRAM (circular buffer for window_size-1 rows)
 * 2. Sliding window registers (window_size x window_size)
 * 3. Pattern matchers for 8 directions (N, NE, E, SE, S, SW, W, NW)
 * 4. Match accumulator
 *)

let () = print_endline "Day 4 stencil engine module defined"
