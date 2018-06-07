(*------------------------------Preamble-------------------------------*)

type color = Black | White | Non;;
let opponent color = match color with
    | Black -> White
    | White -> Black
    | _     -> Non;;

Random.init (int_of_float (1000000. *. (Sys.time () )));;

(*-------------------------------Board---------------------------------*)

(* need w stones to win , a p * q board *)
let init_game () =  let () = print_string "Need how many in a line to win?" in
                    let w = read_int ()in
                    let () = print_newline () in
                    let () = print_string "What is the size of the board?" in
                    let () = print_newline () in 
                    let () = print_string "Vertical: " in
                    let p = read_int () in
                    let () = print_newline () in
                    let () = print_string "Horizontal: " in
                    let q = read_int () in
                    let () = print_newline () in
                    w, p, q;;
 
let w, p, q = init_game ();;

let board = Array.make_matrix p q Non;;

let board_free () =
    let rec aux i j = match i, j with
        | t, _ when t = p   -> true
        | _, t when t = q   -> aux (i + 1) 0
        | _, _ when board.(i).(j) = Non -> aux i (j + 1)
        | _, _  -> false
    in aux 0 0 ;;

let in_board x y =
    0 <= x && 0 <= y && x < p && y < q;;

let neighborhood = [|p / 2; p / 2; q / 2; q / 2|];;

let neighbor i j =
    let new_neighborhood = Array.make 4 0 in
        new_neighborhood.(0) <- max 0 (min neighborhood.(0) (i - 3));
        new_neighborhood.(1) <- min p (max neighborhood.(1) (i + 3));
        new_neighborhood.(2) <- max 0 (min neighborhood.(2) (j - 3));
        new_neighborhood.(3) <- min q (max neighborhood.(3) (j + 3));
        new_neighborhood;;

let new_neighbor i j =
    neighborhood.(0) <- max 0 (min neighborhood.(0) (i - 3));
    neighborhood.(1) <- min p (max neighborhood.(1) (i + 3));
    neighborhood.(2) <- max 0 (min neighborhood.(2) (j - 3));
    neighborhood.(3) <- min q (max neighborhood.(3) (j + 3));;

let restart ()=
	for i = 0 to p-1 do
		for j = 0 to q-1 do
			board.(i).(j) <- Non
        done;
    done;
    neighborhood.(0) <- p / 2;
    neighborhood.(1) <- p / 2;
    neighborhood.(2) <- q / 2;
    neighborhood.(3) <- q / 2;;

(*--------------------------------Move---------------------------------*)

let is_free x y =
	0 <= x && 0 <= y && x < p && y < q && board.(x).(y) = Non;;

let black_move x y =
	if board.(x).(y) <> Non
		then	print_string "not valid" 
        else	board.(x).(y) <- Black;;

let white_move x y =
	if board.(x).(y) <> Non
		then	print_string "not valid"
        else	board.(x).(y) <- White;;

let color_move x y color = match color with
    | Black -> black_move x y
    | White -> white_move x y
    | _     -> print_string "not valid";;

let human_move color = 
    let aux () = 
        let () = print_string "Vertical: " in
        let a = read_int () in 
        let () = print_newline () in
        let () = print_string "Horizontal: " in
        let b = read_int () in
        a, b 
    in
    let rec aux2 = function
        | a, b when is_free a b -> a, b
        | _, _                  -> aux2 (aux ())
    in let i, j = aux2 (aux ()) in
        new_neighbor i j;
        i, j;;

let take_back x y =
	board.(x).(y) <- Non;;

(*--------------------------------Win----------------------------------*)

let tri_insertion tab =
	let l = Array.length tab in
	let rec aux pivot index = match index with
		| _ when pivot >= l	-> ()
		| 0	-> aux (pivot + 1) (pivot + 1)
		| _ when tab.(index) > tab.(index - 1) -> 
                let m = tab.(index) in
					tab.(index) <- tab.(index - 1);
					tab.(index - 1) <- m;
    				aux pivot (index - 1)
		| _	-> aux (pivot + 1) (pivot + 1)
	in aux 1 1; tab;;

let line x y color =
   let rec aux pair func acc = match fst pair, snd pair with
      | a, b when in_board a b && board.(a).(b) = color -> aux (func (a, b)) func (acc + 3)
      | a, b when in_board a b && board.(a).(b) = Non   -> 1 + acc
      | _, _	-> acc
   in
   let aux2 num = match num with
        | t     when t mod 3 = 0 && t < w * 3   -> 0
        | _	-> num
   in
      let num1 = aux (x + 1, y) (function (x, y) -> (x + 1, y)) 0
                + aux (x - 1, y) (function (x, y) -> (x - 1, y)) 0
                + 3
         and
         num2 = aux (x - 1, y - 1) (function (x, y) -> (x - 1, y - 1)) 0
                + aux (x + 1, y + 1) (function (x, y) -> (x + 1, y + 1)) 0
                + 3
         and
         num3 = aux (x, y - 1) (function (x, y) -> (x, y - 1)) 0
                + aux (x, y + 1) (function (x, y) -> (x, y + 1)) 0
	        + 3
         and
         num4 = aux (x + 1, y - 1) (function (x, y) -> (x + 1, y - 1)) 0
         	+ aux (x - 1, y + 1) (function (x, y) -> (x - 1, y + 1)) 0
		+ 3
         in tri_insertion [|aux2 num1; aux2 num2; aux2 num3; aux2 num4|];;

let win x y color =
	(line x y color).(0)>= 3 * w;;

(*-------------------------------Print---------------------------------*)

let print_board () =
    let rec aux i j = match i, j with
        | t, _  when t = p  -> ()
        | _, t  when t = q  -> print_newline ();
                               aux (i + 1) (-1)
        | (-1), (-1)    -> print_char ' '; 
                           print_string " |"; 
                           aux (-1) 0
        | _, (-1)       -> print_int i; 
                           if i < 10 then 
                               print_char ' '; 
                           print_string "|"; 
                               aux i (j + 1)
        | (-1), _       -> print_int j; 
                           print_char ' '; 
                           aux i (j + 1)
        | _, _          -> (match board.(i).(j) with
                            | Black -> print_char '@'
                            | White -> print_char 'O'
                            | _ -> print_char ' ');
                           if j > 9 then 
                               print_char ' '; 
                           print_char '|';
                               aux i (j + 1)
    in aux (-1) (-1); print_newline ();;

let print_place i j =
    let () = print_char '(' in
    let () = print_int i in
    let () = print_string ", " in
    let () = print_int j in
    let () = print_char ')' in
    let () = print_newline () in
    ();;

(*------------------------------Game-on--------------------------------*)

let instruction () =
    let () = print_board () in
    let () = print_int w in
    let () = print_string " in a line to win!" in
    let () = print_newline () in
    print_newline ();;

let rec move aqui black_func white_func = match aqui with 
    | White -> let i, j = white_func White in 
        (match board.(i).(j) with 
            | Non when win i j White    -> white_move i j;
                                        print_board ();
                                        print_string "White Win!!";
                                        print_newline ()
            | Non                       -> white_move i j; 
                                        print_board (); 
                                        print_string "black turn"; 
                                        print_newline (); 
                                        move Black black_func white_func
            | _                         -> print_board (); 
                                        print_string "Move Invalid"; 
                                        print_newline ();
                                        print_string "white turn"; 
                                        print_newline (); 
                                        move White black_func white_func )
    | Black     -> let i, j = black_func Black in
            (match board.(i).(j) with
            | Non     when win i j Black -> black_move i j; 
                                        print_board (); 
                                        print_string "Black Win!!!";
                                        print_newline ()
            | Non                       -> black_move i j; 
                                        print_board ();
                                        print_string "white turn"; 
                                        print_newline (); 
                                        move White black_func white_func
            | _                         -> print_board (); 
                                        print_string "Move Invalid"; 
                                        print_newline ();
                                        print_string "black turn"; 
                                        print_newline (); 
                                        move Black black_func white_func )
    | _     -> print_string "wrong player";;

let gameon black_func white_func = 
    instruction (); 
    match Random.int 2 with
    | 0     -> print_string "Black first"; 
               print_newline (); 
               move Black black_func white_func
    | 1     -> print_string "White first"; 
               print_newline (); 
               move White black_func white_func
    | _     -> print_string "wrong player";;

(*-----------------------------Gloutone--------------------------------*)

let evalue_function_gloutone x y color=
	if not (is_free x y) then 0 else 
	let t = line x y color in match t.(0), t.(1), t.(0) mod 3, t.(1) mod 3 with
        | a, _, _, _    when a >= w * 3 -> 2 * w + 10
        | a, _, _, _    when a <= 5     -> 0
        | a, b, 1, _    when a = b      -> (a - 1) / 3 * 2
        | a, b, 1, _    when a - b = 2  -> (a - 1) / 3 * 2
        | a, b, 1, 0                    -> ((a - 1) / 3 - 1) * 2
        | a, _, 2, _                    -> ((a - 2) / 3) * 2
        | _, _, _, _                    -> 0

let score_gloutone x y color= 
	max (evalue_function_gloutone x y (opponent color)) ((evalue_function_gloutone x y color) + 1);;

(* AI--gloutone *)
let gloutone color =
    if (board_free ()) then ((p / 2, q / 2)) else
    begin
    let rec aux_list i j acc taille max=
        let note = score_gloutone i j color in match i, j with
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
	        let a = Random.int (snd couple) in
	        let rec aux_final j lis = match j with
		        | x 	when x = a	-> List.hd lis
		        | _	-> aux_final (j + 1) (List.tl lis)
	        in aux_final 0 (fst couple)
            in 
            let () = print_place i j in
            i, j
    end;;

(*-----------------------------Minimax---------------------------------*)

let hauteur = ref 2;;

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

(* AI--Minimax *)
let minimax color =
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

(*------------------------------Play-----------------------------------*)

let ai_functions = [| human_move; gloutone; minimax|];;


