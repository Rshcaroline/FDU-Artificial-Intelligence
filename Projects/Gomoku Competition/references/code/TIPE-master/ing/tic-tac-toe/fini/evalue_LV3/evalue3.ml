open Base;;

let hauteur = ref 1;;

(* Score for patterns *)
let add = 
    [|10000; 1000; 10; 10000; 1000; 10|];;

let patterns = 
    [| [|Black; Black; Black; Black; Black|]; 
    [| Non; Black; Black; Black; Black; Non|]; 
    [| Non; Black; Black; Black; Non|]; 
    [|White; White; White; White; White|]; 
    [|Non; White; White; White; White; Non|]; 
    [|Non; White; White; White; Non|] |];;

let positionadd x y = max (p / 2) (q / 2) - max (abs ((p / 2) - x)) (abs ((q / 2) - y));;

let patternmatch x y (dirx, diry) pattern color =
    let n = Array.length pattern in 
    let rec aux i j = function
        | m when m = n  -> 1
        | m when pattern.(m) = Non && m = 0 && board.(i - dirx).(j - diry) = Non
            -> aux i j (m + 1)
        | m when pattern.(m) = Non && m = 0
            -> 0
        | m when pattern.(m) = Non && board.(i).(j) = Non
            -> aux (i + dirx) (j + diry) (m + 1)
        | m when pattern.(m) = color && board.(i).(j) = color
            -> aux (i + dirx) (j + diry) (m + 1)
        | _ -> 0
    in
        match color with
        | _ -> try aux x y 0 with index_out_of_bound -> 0;;

let dir = [| (-1, -1); (-1, 0); (-1, 1); (0, -1); (0, 1); (1, -1); (1, 0); (1, 1) |];;

let local_score i j col =
    let n = Array.length patterns in
    let rec aux score d t= match d with
        | _ when t = n  -> score
        | 7 -> 
            aux (score + patternmatch i j dir.(d) patterns.(t) col * add.(t)) 0 (t + 1)
        | _ -> 
            aux (score + patternmatch i j dir.(d) patterns.(t) col * add.(t)) (d + 1) t
    in aux 0 0 0;;

let note color=
    let rec aux score col x y = match x, y with
        | i, j when i = p   -> score
        | i, j when j = q   -> aux score col (i + 1) 0
        | i, j when board.(i).(j) = Non -> aux score col i (j + 1)
        | i, j when board.(i).(j) = col -> 
                aux (local_score i j col + score + positionadd i j) col i (j + 1)
         | i, j -> aux score col i (j + 1)
    in aux 0 color 0 0 - aux 0 (opponent color) 0 0;;


let rec alpha_beta i j alpha beta color hauteur original = match hauteur with
    | 0 -> [(i, j)], note original
    | _ when i <> -1 && j <> -1 && win i j (opponent color) 
                -> [(i, j)], note original
    | _ ->  let rec aux x y a b acc = match x, y with
            | t, _  when (t = p || b <= a) && color = original   -> acc, a
            | t, _  when (t = p || b <= a)                       -> acc, b
            | _, t  when t = q  -> aux (x + 1) 0 a b acc
            | _, _  when board.(x).(y) <> Non   -> aux x (y + 1) a b acc
            | _, _  ->
                    let () = color_move x y color in
                    let cop = alpha_beta x y a b (opponent color) (hauteur - 1) original in
                    let () = take_back x y in
                    (match color with
                    | c when c = original && a < snd cop   -> 
                            aux x (y + 1) (snd cop) b [(x, y)] 
                    | c when c = original && a = snd cop   ->
                            aux x (y + 1) a b ((x, y)::acc)
                    | c when c = original   ->
                            aux x (y + 1) a b acc
                    | _ when b > snd cop    ->
                            aux x (y + 1) a (snd cop) [(x, y)]
                    | _ when b = snd cop    ->
                            aux x (y + 1) a b ((x, y)::acc)
                    | _     ->
                            aux x (y + 1) a b acc     )
           in
           let couple = aux 0 0 alpha beta [] in
           couple;;

(* AI--lv3 *)
let lv3 color =
    let i, j = 
    if (board_free ()) then ((p / 2, q / 2)) else
        begin
        let couple = alpha_beta (-1) (-1) min_int max_int color !hauteur color
        in
        let a = Random.int (List.length (fst couple)) in
        let rec aux_final j lis = match j with
	        | x 	when x = a	-> List.hd lis
	        | _	    -> aux_final (j + 1) (List.tl lis)
        in aux_final 0 (fst couple);
        end
    in 
    print_place i j;
    new_neighbor i j;
    i, j;;
gameon human_move lv3;;
