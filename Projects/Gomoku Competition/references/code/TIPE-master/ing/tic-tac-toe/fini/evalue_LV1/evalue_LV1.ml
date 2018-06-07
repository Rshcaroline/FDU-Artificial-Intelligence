open Base;;

let power m n =
    let rec aux num puissance acc = match puissance with
        | _ when puissance = 0          -> acc
        | _ when puissance mod 2 = 0    -> aux (num * num) (puissance / 2) acc
        | _                             -> aux (num * num) (puissance / 2) (acc * num)
    in aux m n 1;;

(* evalue_function *)
let evalue_function x y color=
	if not (is_free x y) then 0 else 
	let t = line x y color in match t.(0), t.(1), t.(0) mod 3, t.(1) mod 3 with
        | a, b, _, _    when a > w * 3 - 2 || (a / 3 = b / 3 && a / 3 + 1 >= w)
                       -> power 3 (w + 2)                           (* win *)
        | a, _, _, _    when a <= 5     
                       -> 0                                         (* 1 or <= 1 *)
        | a, b, 1, 1   -> power 3 (a / 3) + power 3 (b / 3)         (* 2 dead 4 *) 
        | a, b, 1, 2   -> power 3 (a / 3) + power 3 ((b + 1) / 3)   (* dead 4 live 3 *)
        | a, b, 1, 0   -> power 3 (a / 3)                           (* dead 4 *)
        | a, _, 2, 0   -> power 3 ((a + 1) / 3)                     (* live 4 *)
        | a, b, 2, 1   -> power 3 ((a + 1) / 3) + power 3 (b / 3)   (* live 4 dead 3 *)
        | a, b, 2, 2   -> power 3 ((a + 1) / 3) + power 3 ((b + 1) / 3) (* 2 live 3 *)
        | _, _, _, _   -> 0

(* the score by evalue_function *)
let score x y color= 
	max (evalue_function x y (opponent color)) ((evalue_function x y color) + 1);;

(* AI *)
let lv1 color =
    let rec aux_list i j acc taille max=
        let note = score i j color in match i, j with
			| t, _	when t = p	-> acc, taille
			| _, t	when t = q	-> aux_list (i + 1) 0 acc taille max
			| _, _	when note > max	-> 
									aux_list i (j + 1) [(i, j)] 1 note
			| _, _	when note = max	-> 
									aux_list i (j + 1) ((i, j)::acc) (taille + 1) max
			| _, _	-> aux_list i (j + 1) acc taille max
	in
	let couple = aux_list 0 0 [] 0 0 in
        let i, j = 
        if (board_free ()) then ((p / 2, q / 2)) else
        begin
	        let a = Random.int (snd couple) in
	        let rec aux_final j lis = match j with
		        | x 	when x = a	-> List.hd lis
		        | _	-> aux_final (j + 1) (List.tl lis)
	        in aux_final 0 (fst couple)
        end
        in 
        let () = print_char '('in
        let () = print_int i in
        let () = print_string ", " in
        let () = print_int j in
        let () = print_char ')' in
        let () = print_newline () in
        i, j;;

gameon lv1 human_move;;
