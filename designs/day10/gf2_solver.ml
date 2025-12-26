(* Day 10: GF(2) Gaussian Elimination *)
open Hardcaml
open Signal

module I = struct
  type 'a t = {
    clock : 'a;
    clear : 'a;
    start : 'a [@bits 1];
    load_valid : 'a [@bits 1];
    load_row : 'a [@bits 8];
    load_data : 'a [@bits 64];
  } [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t = {
    solution : 'a [@bits 64];
    done_ : 'a [@bits 1];
  } [@@deriving sexp_of, hardcaml]
end

let create (scope : Scope.t) (i : Signal.t I.t) : Signal.t O.t =
  let _spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in
  (* TODO: Implement matrix BRAM + XOR array + FSM *)
  { O.solution = Signal.zero 64
  ; done_ = Signal.gnd
  }
