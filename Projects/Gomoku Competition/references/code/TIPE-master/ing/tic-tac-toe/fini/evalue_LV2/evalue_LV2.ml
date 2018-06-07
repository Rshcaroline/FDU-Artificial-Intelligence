open Base;;

(* evalue_function *)
let evalue_function x y color=
	if not (is_free x y) then 0 else 
	let t = line x y color in match t.(0), t.(1), t.(0) mod 3, t.(1) mod 3 with
        | a, _, _, _    when a >= w * 3 -> 2 * w + 10
        | a, _, _, _    when a <= 5     -> 0
        | a, b, 1, _    when a = b      -> (a - 1) / 3 * 2
        | a, b, 1, _    when a - b = 2  -> (a - 1) / 3 * 2
        | a, b, 1, 0                    -> ((a - 1) / 3 - 1) * 2
        | a, _, 2, _                    -> ((a - 2) / 3) * 2
        | _, _, _, _                    -> 0;;

(* the score by evalue_function *)
let score x y color= 
    evalue_function x y color - evalue_function x y (Base.opponent color);;

(* AI *)
let turn color =
    let rec aux_list i j acc taille max=
        let note = score i j color in match i, j with
			| t, _	when t = p	-> acc, taille
			| _, t	when t = q	-> aux_list (i + 1) 0 acc taille max
			| _, _	when note > max	-> 
									aux_list i (j + 1) [(i, j)] 1 note
			| _, _	when note = max	-> 
									aux_list i (j + 1) ((i, j)::acc) (taille + 1)max
			| _, _	-> aux_list i (j + 1) acc taille max
	in
	let couple = aux_list 0 0 [] 0 0 in
        if (snd couple = p * q ) then ((p / 2, q / 2)) else
        begin
	        let a = Random.int (snd couple) in
	        let rec aux_final j lis = match j with
		        | x 	when x = a	-> List.hd lis
		        | _	-> aux_final (j + 1) (List.tl lis)
	        in aux_final 0 (fst couple)
        end;;

gameon human_move turn;;
