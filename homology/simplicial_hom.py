'''
The code developed is inspired from "Computational Algebriac Topology Lecture Notes" written by Vidit Nanda
The notes are given here https://people.maths.ox.ac.uk/nanda/cat/TDANotes.pdf
'''
import numpy as np

class Simplicial_Complex:
	'''
	Return the dimension of a simplex, which is just the # of vertices - 1
	'''
	@staticmethod
	def dim(simplex) -> int:
		return len(simplex) - 1

	'''
 	For a simplex, check if the class has all subsets of this simplex one dimension lower 
  	'''
	def contains_subsets_of(self, simplex):
		# Vertices have no proper subset but the empty set
		if Simplicial_Complex.dim(simplex) == 0:
			return True
  
		lower_simplices = self.simplices[Simplicial_Complex.dim(simplex) - 1]
  
		# Generate all the faces for the simplex
		face = simplex
		for i in range(Simplicial_Complex.dim(simplex) + 1):
			vert = face.pop(i)
			is_face_in = False
			for lower_simplex in lower_simplices:
				if set(lower_simplex) == set(face):
					is_face_in = True
			face.insert(i, vert)
   
			if not is_face_in:
				return False

		# All possible faces are already in the complex
		return True

	'''
	Check if the simplicial complex given is valid
	'''
	def is_valid(self):
		# For every simplex, check if all subsets of it is contained within the class
		for cur_dim in range(0, self.dim + 1):
			for simplex in self.simplices[cur_dim]:
				if not self.contains_subsets_of(simplex):
					return False
		return True


	'''
	Initiate a simplicial complex
	'''
	def __init__(self, complex_as_list):
		# Store the list
		self.complex_as_list = complex_as_list
    
  		# Get the dimension of the simplicial complex (the maximum of the dimensions of all the simplices)
		self.dim = 0
		for simplex in complex_as_list:
			if Simplicial_Complex.dim(simplex) > self.dim:
				self.dim = Simplicial_Complex.dim(simplex)

		# Seperate the list into different dimension

		# Create an array that holds simplices of 0th dimension to the highest dimension 
		self.simplices = []
		for cur_dim in range(self.dim + 1):
			self.simplices.append([])
			for simplex in complex_as_list:
				if Simplicial_Complex.dim(simplex) == cur_dim:
					self.simplices[cur_dim].append(simplex)
		# Then confirm that the list given is indeed a simplicial complex
		assert(self.is_valid())
  
		# After confirming it is indeed a simplicial complex, compute the boundary operators
		self.compute_boundary_operators()
  
		# After computing the boundary operators, compute the homology group
		self.compute_homology()
	
	'''
 	Auxillary function that determines if simplex_two, a subset of simplex_one, has the same orientation
	If simplex_two appears in simplex_one in the same order, then it returns True. Otherwise, the orientation is reversed,
	and so it return False.
	
	Since the inputs given are guaranteed to be a subset of one another created from obsolving 
  	'''
	def oriented(self, simplex_one, simplex_two):
		# Found on stackoverflow, unfortunately can't find it again. No idea how it works, but it does the job
		def generate_list(l1, l2):
			for element in l1:
				if element in l2:
					yield element
		for x1, x2 in zip(generate_list(simplex_one, simplex_two), generate_list(simplex_two, simplex_one)):
			if x1 != x2:
				return False
		return True

	'''
	Compute the boundary operators 
 	'''
	def compute_boundary_operators(self):
		self.boundary_operator = []
  
		# delta_0 is just mapping all points to nothing
		self.boundary_operator.append(np.ones((1, len(self.simplices[0]))))

		# delta_i is just C_i to C_i-1
		for i in range(1, self.dim + 1):
			upper_simplices = self.simplices[i]
			lower_simplices = self.simplices[i - 1]
			self.boundary_operator.append(np.zeros((len(lower_simplices), len(upper_simplices))))

			for low_idx in range(len(lower_simplices)):
				lower_simplex = lower_simplices[low_idx]			
				for upper_idx in range(len(upper_simplices)):
					upper_simplex = upper_simplices[upper_idx]
    
					# if lower_simplex is a subset of upper_simplex, then it is a face of the upper_simplex
					if set(upper_simplex) >= set(lower_simplex):

						# if the orientation of the lower_simplex is the same as the orientation of the upper_simplex
						# multiply the incidence
						if self.oriented(upper_simplex, lower_simplex):
							(self.boundary_operator[i])[low_idx][upper_idx] = 1
						else:
							(self.boundary_operator[i])[low_idx][upper_idx] = -1
       
		# the final boundary operator d_n+1: 0->C_n is simply every basis element of C_n 
		self.boundary_operator.append(np.ones((len(self.simplices[self.dim]), 1)))		
 
	'''
	Find Smith Normal Form of A.
	'''
	@staticmethod
	def smith_normal_form(A):
		n = len(A)
		m = len(A[0])
		Dtop = np.hstack( (np.eye(n), A.copy()) )
		Dbot = np.hstack( (np.zeros((m, n)), np.eye(m)) )
		D = np.vstack( (Dtop, Dbot) )
  
		rank = 0
		
		# Apply a modified form of the RREF algorithm, which starts at index n (or where A resides)
		# Modified RREF algorithm given by https://math.stackexchange.com/questions/3073083/how-to-reduce-matrix-into-row-echelon-form-in-numpy
		for col in range(n, n + min(m, n)):
				
			# For the current row, search for the elements in A are nonzero
			i = col - n
			for j in range(i, n):
				if D[j][col] != 0:
					rank = rank + 1
					i = j
					break
			else:
				# All the elements in this row are zero, so continue
				continue
			
			# Swap the row at i with the row associated with the column
			irow = D[i].copy()
			D[i] = D[col - n]
			D[col - n] = irow
   
			# Reduce the row
			D[col - n] = D[col - n]/D[col - n][col]
   
			# Now that rows are swapped, put zeros on top and bottom
			for row in range(0, n):
				if row != col - n and D[row][col] != 0:
					D[row] = D[row] - D[col - n] * D[row][col]
     
		# At this point, all matrices should be reduced in A, but if columns in A > rows in A, it
		# might be the case that A still isn't in Smith Normal Form
		# The solution in this case is simple and it's to get set to zeros the remaining columns
		if m > n:
			D[:, n + n:] = D[:, n + n:] * 0
  
		# get P and Q
		P = D[0:n,0:n]
		Q = D[n:, n:]
  
		return rank, P, Q

	'''
 	Find the RREF of the matrix
  	'''
	@staticmethod
	def rref(A):
		mat = A.copy()
		n = len(A)
		m = len(A[0])
		for col in range(0, m):
			# For the current row, search for the elements in A are nonzero
			i = col
			for j in range(i, n):
				if mat[j][col] != 0:
					i = j
					break
			else:
				# All the elements in this row are zero, so continue
				continue
			
   			# Swap the row at i with the row associated with the column
			irow = mat[i].copy()
			mat[i] = mat[col]
			mat[col] = irow
   
			# Reduce the row
			mat[col - n] = mat[col - n]/mat[col - n][col]
   
			# Now that rows are swapped, put zeros on top and bottom
			for row in range(0, n):
				if row != col - n and mat[row][col] != 0:
					mat[row] = mat[row] - mat[col] * mat[row][col]
		return mat

	'''
 	For every boundary operator (except the 0th), compute the Smith Normal Form and get the corresponding P, Q, and D
  
	The 0th homology group is simply the basis of the C_0
  	'''
	def compute_homology(self):
		# the boundary operator d_0: C_0 -> 0
		P = {}
		Q = {}
		rank = {}
		for i in range(0, self.dim + 2):
			ranki, Pi, Qi = Simplicial_Complex.smith_normal_form(self.boundary_operator[i])
   
			P[i] = Pi
			Q[i] = Qi
			rank[i] = ranki
			#P.append(Pi)
			#Q.append(Qi)
			#rank.append(ranki)

		# Get Z
		Z = {}
		for key in P:
			Z[key - 1] = np.linalg.inv(P[key])[:, key:]
   
		# Get B
		B = {}
		for key in Q:
			B[key] = (Q[key])[:, :len(Q[key]) - rank[key]]

  
		# get G
		G = {}
		H = {}
		for key in B:
			if key in Z:
				G[key] = np.hstack( (B[key], Z[key]) )
    			# reduce B[i] and Z[i]
				H[key] = np.hstack( (Simplicial_Complex.rref(B[key]), Simplicial_Complex.rref(Z[key])) )
				print("\n\n\n")
				print(B[key])
				print(Z[key])
   			
		...

if __name__ == '__main__':
    # valid simplicial complex
	print("Triangle\n")
	K_list = [['A'], ['B'], ['C'], ['A', 'B', 'C'], ['A', 'B'], ['B', 'C'], ['C', 'A'], ['D']]
	K = Simplicial_Complex(K_list)
 	
	# not valid simplicial complex, throws assertion error
	# K_prime_list = [['A'], ['B'], ['C'], ['A', 'B', 'C'], ['A', 'B'], ['B', 'C']]
	# K_prime = Simplicial_Complex(K_prime_list)
 
	print("\n\n\nLine\n")
	K_line_list = [['A'], ['B'], ['C'], ['D'], ['E'], ['A', 'B'], ['B', 'C'], ['C', 'D'], ['D', 'E']]
	K_line = Simplicial_Complex(K_line_list)

	print("\n\n\nTorus\n")
	
	torus_vertices = [[chr(ord('A') + i)] for i in range(9)]
	torus_edges = [['A', 'B'], ['B', 'E'], ['E', 'A'], ['A', 'D'], ['D', 'E'],
               		['B', 'C'], ['C', 'F'], ['F', 'B'], ['B', 'E'], ['E', 'F'],
                 	['C', 'A'], ['A', 'D'], ['D', 'C'], ['C', 'F'], ['F', 'D'],
	
                  	['D', 'E'], ['E', 'H'], ['H', 'D'], ['D', 'G'], ['G', 'H'],
                   	['E', 'F'], ['F', 'I'], ['I', 'E'], ['E', 'H'], ['H', 'I'],
                    ['F', 'D'], ['D', 'G'], ['G', 'F'], ['F', 'I'], ['I', 'G'],
                    
                    ['G', 'H'], ['H', 'B'], ['B', 'G'], ['G', 'A'], ['A', 'B'],
                    ['H', 'I'], ['I', 'C'], ['C', 'H'], ['H', 'B'], ['B', 'C'],
                    ['I', 'G'], ['G', 'A'], ['A', 'I'], ['I', 'C'], ['C', 'A']
                    ]
	# get rid of duplicate edges
 
	torus_faces = [['A', 'B', 'E'], ['E', 'A', 'D'],
                	['B', 'C', 'F'], ['F', 'B', 'E'],
                 	['C', 'A', 'D'], ['D', 'C', 'F'],

					['D', 'E', 'H'], ['H', 'D', 'G'],
			     	['E', 'F', 'I'], ['I', 'E', 'H'],
					['F', 'D', 'G'], ['G', 'F', 'I'],

     				['G', 'H', 'B'], ['B', 'G', 'A'],
			     	['H', 'I', 'C'], ['C', 'H', 'B'],
					['I', 'G', 'A'], ['A', 'I', 'C']
                  	]
	torus = torus_vertices + torus_edges + torus_faces
	torus = list(map(list, set(map(tuple, torus))))
	#print(torus)
	#torus_complex = Simplicial_Complex(torus)

	#Simplicial_Complex.smith_normal_form(np.array([[1, 2, 3], [4, 5, 6]]))
	Simplicial_Complex.smith_normal_form(np.array([[1, 2, 3, 4], [5, 6, 7, 8]]))

	#K_line_list = [['A'], ['B'], ['C'], ['D'], ['E'], ['A', 'B'], ['B', 'C'], ['C', 'D'], ['D', 'E']]
	#K_line = Simplicial_Complex(K_line_list)
