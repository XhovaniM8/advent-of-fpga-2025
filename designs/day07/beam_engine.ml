(* 
 * Day 7: Event-Driven Beam Propagation Engine
 * 
 * Architecture:
 *   Event Queue (BRAM FIFO) -> Time Surface Check -> Beam Processor -> Output Events
 * 
 * Event format (32 bits):
 *   [31:16] timestamp
 *   [15:14] direction (N=0, E=1, S=2, W=3)
 *   [13:7]  y coordinate
 *   [6:0]   x coordinate
 * 
 * Resources (estimated for 143x143 grid):
 *   BRAM: ~180KB (time surface + queue + grid ROM)
 *   LUTs: ~500
 *   Fmax: ~200MHz
 *)

open Hardcaml
open Signal

module BeamEvent = struct
  type 'a t = {
    x : 'a [@bits 7];
    y : 'a [@bits 7];
    direction : 'a [@bits 2];
    timestamp : 'a [@bits 16];
  } [@@deriving sexp_of, hardcaml]
end

module I = struct
  type 'a t = {
    clock : 'a;
    clear : 'a;
    start : 'a [@bits 1];
    start_x : 'a [@bits 7];
    start_y : 'a [@bits 7];
    start_dir : 'a [@bits 2];
  } [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t = {
    done_ : 'a [@bits 1];
    energized_count : 'a [@bits 16];
    cycle_count : 'a [@bits 32];
  } [@@deriving sexp_of, hardcaml]
end

(* TODO: Implement create function
 * 
 * let create (i : Signal.t I.t) : Signal.t O.t =
 *   let open Signal in
 *   let reg_spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in
 *   
 *   (* Event queue FIFO *)
 *   (* Time surface BRAM *)
 *   (* Grid ROM *)
 *   (* Beam processor FSM *)
 *   
 *   { O.done_ = ...
 *   ; energized_count = ...
 *   ; cycle_count = ...
 *   }
 *)

let () = print_endline "Day 7 module structure defined"
