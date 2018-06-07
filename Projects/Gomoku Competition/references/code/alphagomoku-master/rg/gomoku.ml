open Format

module IP = struct
  type t = int * int
  let compare = compare
end
module IPS = Set.Make (IP)

type board = IPS.t * IPS.t (* (to move now, to move next) *)

let size = 19

let empty_board = (IPS.empty, IPS.empty)
let initial_move = (size / 2 + 1, size / 2 + 1)
let initial_board = (IPS.empty, IPS.add initial_move IPS.empty)

let game_count = ref 0

type state =
  { s_probability : float
  ; s_board : board
  ; s_previous : state option }

let print x =
  incr game_count;
  let fn = sprintf "game%08d.txt" !game_count in
  printf "@[saving %s@.@]" fn;
  let ch = open_out fn in
  let out = formatter_of_out_channel ch in
  let rec f ms { s_board; s_previous; _ } = match s_previous with
    | None -> initial_move :: ms
    | Some ({ s_board = p; _ } as s_previous) ->
        let ms =
          (match s_board, p with (a, b), (c, d) -> IPS.choose (IPS.diff b c))
          :: ms in
        f ms s_previous in
  let ms = f [] x in
  let pm (x, y) = fprintf out "@[%d,%d@]@\n" x y in
  List.iter pm ms;
  let xx, oo = x.s_board in
  for i = 1 to size do begin
    fprintf out "c ";
    for j = 1 to size do
      fprintf out
        (if IPS.mem (i,j) xx then "x"
        else if IPS.mem (i,j) oo then "o"
        else ".")
    done;
    fprintf out "@."
  end done;
  close_out_noerr ch

let pick xs =
  let rec f r ys = function
    | [] -> raise Not_found
    | [x] -> (x, ys)
    | x :: xs ->
(*         printf "@[%b %f %f@.@]" (r <= x.s_probability) r x.s_probability; *)
        if r <= x.s_probability
        then (x, xs@ys)
        else f (r -. x.s_probability) (x :: ys) xs in
  f (Random.float 1.0) [] xs

(*
let pick = function
  | [] -> raise Not_found
  | x :: xs -> (x, xs)
*)

let neighbours =
  let xs = ref [] in
  for i = -2 to 2 do
    for j = -2 to 2 do
      if i<>0 || j <> 0 then xs := (i, j) :: !xs
    done
  done;
  !xs

let is_winner (x, y) xys =
  let ds = [(0, 1); (1, 1); (1, 0); (1, -1)] in
  let rec count (dx, dy) n (x, y) =
    if IPS.mem (x, y) xys
    then count (dx, dy) (n+1) (x+dx, y+dy)
    else n in
  let one_dir (dx, dy) =
    count (-dx, -dy) 0 (x, y) + count (dx, dy) 0 (x, y) > 5 in
  List.exists one_dir ds

let successors old_state =
  let a, b = old_state.s_board in
  let c = IPS.union a b in
  let nearby (x, y) =
    let f (i, j) = IPS.mem (x + i, y + j) c in
    not (IPS.mem (x, y) c) && List.exists f neighbours in
  let rec loop i j ms = match i, j with
    | 0, _ -> ms
    | _, 0 -> loop (i-1) size ms
    | _ -> loop i (j-1) (if nearby (i, j) then (i, j) :: ms else ms) in
  let ms = loop size size [] in
  let s_probability =
    old_state.s_probability /. float_of_int (List.length ms) in
  let one_move (x, y) =
    let na = IPS.add (x, y) a in
    ( is_winner (x, y) na
    , { s_probability
      ; s_board = (b, na)
      ; s_previous = Some old_state } ) in
  List.map one_move ms

let rec play n xs =
  if n <= 0 then () else begin
    let x, xs = pick xs in
    let xs = [] in (* hack *)
    let rec f n xs = function
      | [] -> play n xs
      | (true, y) :: ys -> print y; f (n-1) xs ys
      | (false, y) :: ys -> f n (y :: xs) ys in
    f n xs (successors x)
  end

let () =
  printf "@[";
  for i = 1 to 1000000 do
    play 1 [{ s_probability = 1.0; s_board = initial_board; s_previous = None }]
  done;
  printf "@.@]"

