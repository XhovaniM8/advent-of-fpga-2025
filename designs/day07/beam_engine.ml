(* Day 7: Event-Driven Beam Propagation *)
open Hardcaml
open Signal

module I = struct
  type 'a t = {
    clock : 'a;
    clear : 'a;
    start : 'a [@bits 1];
    start_x : 'a [@bits 8];
    start_y : 'a [@bits 8];
    start_dir : 'a [@bits 2];
  } [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t = {
    energized_count : 'a [@bits 16];
    done_ : 'a [@bits 1];
  } [@@deriving sexp_of, hardcaml]
end

let create (scope : Scope.t) (i : Signal.t I.t) : Signal.t O.t =
  let _spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in
  (* TODO: Implement event queue + time surface + beam processor *)
  { O.energized_count = Signal.zero 16
  ; done_ = Signal.gnd
  }
