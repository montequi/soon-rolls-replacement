pruebaspade.py
It is the simulator, it has the backatracking algorithm implemented and the ABT version as well. It uses the Python versión 3.7.2. Requires the libraries json, os, operator, random, func_timeout, numpy, decimal, pade, copy, subprocess, collections, psutil, signal and time. It uses conjuntoalmacenado.json that has the rolls and the positions of the initial set of rolls or a random set is generated depending on the selection of the user. It needs a configuration file cilindros.json with the types of jobs to perform, the shapes of the rolls, the types of rolls to generate and gives as output sample.json is the solution of the backtracking algorithm or of a vein of the ABT algorithm for a particular job. tiemposmedidos.json has the time it lasts in performing the algorithm. 
cilindrosfinal.json indicates how the state of the rolls and its positions after rolling each of the scheduled jobs. 
diametrosmedios.json provides information about the average diameter, the median, the variance and the mode for each of the types of rolls (geometry and shape) after rolling. definitivostotales.json has the rolls used for each of the rollings.
datos14.json is the entry of lanzar.py. It has the compatible rolls and the constraints among stands.
resultadoabt2.json has the result of executing lanzar.py. It indicates for each of the stands considered the diameter and the codes used in a vein, also it indicates the number of nogoods and the number of oks for each of the stands.
compras.json is an output file that indicates the rolls to buy.
rectificados.json indicates for each scheduled job the percentage of rolls that have been rectified.


lanzar.py
It executes the ABT algorithm. It uses as entry datos14.json (It has the compatible rolls and the constraints among stands) and has as output resultadoabt2.json (it indicates for each of the stands considered the diameter and the codes used in a vein, also it indicates the number of nogoods and the number of oks for each of the stands). It uses the Python version 3.7.2. Requires the libraries json, signal, os, psutil, numpy, func_timeout, random, pade and copy.


nuevainterfaz.py
It is the interface. It uses the auctions algorithm by calling auctionsinterfaznuevaversion3.py for repeating the set of jobs the number of specified times and auctionsinterfaznuevaversion.py for performing the set of jobs once. It uses the Python version 3.7.2. Requires the libraries tkinter, os, json, time, psutil, PIL, matplotlib.pyplot, numpy and threading. 


auctionsnuevainterfaz.py
It is the version of the auctions algorithm for performing a set of jobs. It uses the Python version 3.7.2. Requires the libraries json, os, decimal, numpy, random, copy, subprocess, pickle, pandas, math, statistics, time and sys. It uses two initial configuration files trabajos.json and conjuntoalmacenado.json, an intermediate file salidarandomfores.json and a final file salidaparagraficasnueva0.json. 


auctionsnuevainterfaz3.py
It is the version of the auctions algorithm for performing a repeated set of jobs. It uses the Python version 3.7.2. Requires the libraries json, os, decimal, numpy, random, copy, subprocess, pickle, pandas, math, statistics, time and sys. It uses two initial configuration files trabajos.json and conjuntoalmacenadointerfaz.json, an intermediate file salidarandomfores.json and a final file salidaparagraficasnueva0.json. 


auctions15maquinas.py
It is the version of the auctions algorithm. It uses the Python version 3.7.2. Requires the libraries json, os, decimal, numpy, random, copy, subprocess, pickle, pandas, math, statistics, time and sys. It uses two initial configuration files trabajos.json and conjuntoalmacenado.json, an intermediate file salidarandomfores.json and different final files salidaparagraficasnueva0.json, salidaparagraficasnueva1.json… depending on how many times the algorithm is repeated for the jobs scheduled. 


trabajos.json
It has the different jobs scheduled to be done, with the tons, the quality of the material, its duration and the stands involved, including for each stand the number, the geometry and the shape, the constraints of each job. A constraint includes the two stands involved, the type, the quantity and the factor. It has the different geometries and shapes for each stand as well, the measures of the rolls, the different possible qualities of the rolls and the cost of Rolling with each quality.


conjuntoalmacenado.json
It has the roll set and the positions.


conjuntoalmacenadointerfaz.json
It has the roll set and the positions for performing a repeated set of jobs.


salidarandomfores.json
It has for each stand how much the rolls would be reduced using the model developed.


salidaparagraficasnueva0.json
It has the jobs that have been performed, the rounds the algorithm has done with the winner agent of each round, the cost of the winner agent, the agents involved in the algorithm and for each agent the diameters of the rolls selected, the data of the rolls selected, the costs, the cost of rolling with each roll, the diameter reductions, the volume reductions, the total volumen reduction, the average diameter, the average diameter reduction for each roll, the average volume reduction, the average cost, the standard deviation of the diameters, the standard deviation of the diameters reduction, the standard deviation of the costs and the standard deviation of the volume reductions. It also includes the number of broken rolls for each stand in the job and the total number of broken rolls for each stand given the jobs performed until that job.
