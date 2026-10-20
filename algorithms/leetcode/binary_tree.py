"""
Given the root of a binary tree, return the length of the diameter of the tree.

The diameter of a binary tree is the length of the longest path between any two nodes in a tree. This path may or may not pass through the root.

The length of a path between two nodes is represented by the number of edges between them.

"""


# Definition for a binary tree node.

# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

 
 # this is the answer:
        
class Solution:
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        """
        :type root: TreeNode
        :rtype: int
        """
        self.dia = 0
        
        def height(root):
            if not root: # does this mean not a root or goes to the leaves (which have no childern)?
                return 0
            left, right = height(root.left), height(root.right)
            self.dia = max(self.dia, left + right)
            return 1 + max(left, right)
            
        height(root)
        return self.dia



## test the answer:

# create a node:

class TreeNode:
    def __init__(self, val = 0, left = None, right = None):
        self.left = left
        self.right = right
        self.data = val
        
    def insert(self, val):
        if self.val:
            if self.left < val:
                if self.left is not None:
                    self.left = TreeNode(val)
                else:
                    self.left.insert(val)
            else:
                if self.right is not None:
                    self.right = TreeNode(val)
                else:
                    self.right.insert(val)
        else:
            self.val = val
            
            
    def PrintTree(self):
        if self.left:
            self.left.PrintTree()
        
        print(self.val)
        
        if self.right:
            self.right.PrintTree()
            

        
        
        
        
        
        
        
        
        
        
        
        
        

