open Hardcaml
open Signal

module I = struct
  type 'a t =
    { clock : 'a
    ; clear : 'a
    ; a : 'a [@bits 8]
    ; b : 'a [@bits 8]
    }
  [@@deriving sexp_of, hardcaml]
end

module O = struct
  type 'a t = { sum : 'a [@bits 8] } [@@deriving sexp_of, hardcaml]
end

let create _scope (i : _ I.t) =
  let sum = i.a +: i.b in
  { O.sum }
