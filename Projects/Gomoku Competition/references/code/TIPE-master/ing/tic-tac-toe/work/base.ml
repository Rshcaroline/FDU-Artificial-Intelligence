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
        new_neighborhood.(0) <- max 0 (min neighborhood.(0) (i - 2));
        new_neighborhood.(1) <- min p (max neighborhood.(1) (i + 2));
        new_neighborhood.(2) <- max 0 (min neighborhood.(2) (j - 2));
        new_neighborhood.(3) <- min q (max neighborhood.(3) (j + 2));
        new_neighborhood;;

let new_neighbor i j =
    neighborhood.(0) <- max 0 (min neighborhood.(0) (i - 2));
    neighborhood.(1) <- min p (max neighborhood.(1) (i + 2));
    neighborhood.(2) <- max 0 (min neighborhood.(2) (j - 2));
    neighborhood.(3) <- min q (max neighborhood.(3) (j + 2));;

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
