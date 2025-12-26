(* Day 12: Dancing Links Exact Cover Solver *)
open Hardcaml
open Signal

module I = struct
  type 'a t = {
    clock : 'a;
    clear : 'a;
    start : 'a [@bits 1];
  } [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t = {
    solution_valid : 'a [@bits 1];
    solution_row : 'a [@bits 10];
    done_ : 'a [@bits 1];
  } [@@deriving sexp_of, hardcaml]
end

let create (scope : Scope.t) (i : Signal.t I.t) : Signal.t O.t =
  let _spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in
  (* TODO: Implement node BRAM + cover/uncover FSM *)
  { O.solution_valid = Signal.gnd
  ; solution_row = Signal.zero 10
  ; done_ = Signal.gnd
  }
