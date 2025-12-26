(* Day 4: Stencil Pattern Matcher *)
open Hardcaml
open Signal

module I = struct
  type 'a t = {
    clock : 'a;
    clear : 'a;
    char_valid : 'a [@bits 1];
    char_data : 'a [@bits 8];
    row_end : 'a [@bits 1];
  } [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t = {
    match_count : 'a [@bits 16];
    done_ : 'a [@bits 1];
  } [@@deriving sexp_of, hardcaml]
end

let create (scope : Scope.t) (i : Signal.t I.t) : Signal.t O.t =
  let _spec = Reg_spec.create ~clock:i.clock ~clear:i.clear () in
  (* TODO: Implement line buffer + sliding window + pattern matchers *)
  { O.match_count = Signal.zero 16
  ; done_ = Signal.gnd
  }
