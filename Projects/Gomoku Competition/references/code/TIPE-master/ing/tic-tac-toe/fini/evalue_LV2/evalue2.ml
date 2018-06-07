open Base;;
let hauteur = ref 2;;

let puissance a b =
    let rec aux c d e = match d with
        | 0                     -> e
        | t when t mod 2 = 0    -> aux (c * c) (d / 2) (e)
        | t                     -> aux (c * c) (d / 2) (e * c)
    in aux a b 1;;
        
let score_max = puissance 10 (w + 2);;

(* evalue_function *)
let evalue_function x y color=
	let t = line x y color in match t.(0), t.(1), t.(0) mod 3, t.(1) mod 3 with
    (* win case *)
        | a, _, _, _    when a >= w * 3 -> puissance 10 (w + 1)
    (* live 1 or less *)
        | a, _, _, _    when a <= 5     -> 0
    (* dead a/3 dead a/3 *)
        | a, b, 1, _    when a = b      -> 
                puissance 10 ((a - 4) / 3) + puissance 5 ((a - 7) / 3)
    (* dead a/3 live a/3 - 1 *)
        | a, b, 1, _    when a - b = 2  -> puissance 10 ((a - 4) / 3)
    (* dead a/3 *)
        | a, b, 1, _                    -> 
                puissance 10 ((a - 4) / 3) - puissance 5 ((a - 7) / 3)
    (* live a/3 live a/3 *)
        | a, b, 2, 2    when a = b      -> puissance 10 ((a - 2) / 3)
    (* live a/3 dead a/3 *)
        | a, b, 2, 1    when a - b = 1  -> 
                puissance 10 ((a - 2) / 3) - puissance 3 ((a - 5) / 3)
    (* live a/3 *)
        | a, _, 2, _                    -> 
                puissance 10 ((a - 2) / 3) - puissance 5 ((a - 5) / 3)
        | _, _, _, _                    -> 0;;

(* the score by evalue_function *)
let score x y color = 
    evalue_function x y color - evalue_function x y (opponent color);;


let rec alpha_beta i j a b color hauteur original = match hauteur with
    | 1 -> score i j original
    | _ -> let () = color_move i j color in
           let rec aux x y c d max = match x, y with
            | t, _  when t = neighborhood.(1)  -> max
            | _, t  when t = neighborhood.(3)  -> aux (x + 1) neighborhood.(2) c d max
            | _, _  when board.(x).(y) <> Non   -> aux x (y + 1) c d max
            | _, _  ->  let z =  
                        -(alpha_beta x y (-d) (-c) (opponent color) (hauteur - 1) original)
                        in
                        (match z with
                            | t when t >= b     -> t
                            | t when t > a      -> aux x (y + 1) t d t
                            | t when t > max    -> aux x (y + 1) c d t
                            | _                 -> aux x (y + 1) c d max)
           in
           let score = aux neighborhood.(0) neighborhood.(2) a b min_int in
           let () = take_back i j in
           score;;

(* AI *)
let turn color =
    let rec aux_list i j acc taille max = match i, j with
			| t, _	when t = neighborhood.(1) -> acc, taille
			| _, t	when t = neighborhood.(3) -> 
                    aux_list (i + 1) neighborhood.(2) acc taille max
            | _, _  when board.(i).(j) <> Non   -> 
                    aux_list i (j + 1) acc taille max
            | _, _  when win i j color  -> [(i, j)], 1
            | _, _  -> 
                    let note = -(alpha_beta i j min_int max_int color !hauteur color) in 
                    (match note with
                        | t when t > max ->
                                    aux_list i (j + 1) [(i, j)] 1 t
                        | t when t = max ->
                                    aux_list i (j + 1) ((i, j)::acc) (taille + 1) max
                        | _ -> aux_list i (j + 1) acc taille max)
	in
	let couple = aux_list neighborhood.(0) neighborhood.(2) [] 0 (-score_max) in
        let i, j = 
        if (board_free ()) then ((p / 2, q / 2)) else
        begin
            let rec aux_print lis = match lis with
                | []    -> print_int (snd couple)
                | t::q  -> print_int (fst t); print_string ", "; print_int (snd t); print_newline (); aux_print q
            in let () = aux_print (fst couple) in
	        let a = Random.int (snd couple) in
	        let rec aux_final j lis = match j with
		        | x 	when x = a	-> List.hd lis
		        | _	-> aux_final (j + 1) (List.tl lis)
            in aux_final 0 (fst couple);
        end
        in 
        print_place i j;
        new_neighbor i j;
        i, j;;

let score_board = Array.make_matrix p q 0;;
let note color hauteur =
    for i = 0 to p - 1 do
        for j = 0 to q - 1 do
            if board.(i).(j) = Non then
            score_board.(i).(j) <- alpha_beta i j (-score_max) score_max color hauteur color
        done
    done;;
