#!/usr/bin/env python3
"""
Generate synthetic datasets for group theory benchmarks.
Uses sympy.combinatorics to ensure mathematical correctness.
"""

import json
import random
from typing import List, Dict, Any, Tuple
from sympy.combinatorics import SymmetricGroup, AlternatingGroup, DihedralGroup, CyclicGroup
from sympy.combinatorics.perm_groups import PermutationGroup
from sympy.combinatorics.permutations import Permutation
import os

class GroupTheoryDataGenerator:
    """Generator for group theory benchmark datasets."""
    
    def __init__(self, seed: int = 42):
        """Initialize with random seed for reproducibility."""
        random.seed(seed)
        self.generated_groups = set()  # Track generated groups to avoid duplicates
        self.used_questions = set()  # Track generated questions to avoid duplicates
        
    def _get_group_signature(self, group: PermutationGroup) -> str:
        """Get a unique signature for a group to enable deduplication."""
        # Use order, degree, and sorted generator strings as signature
        gens = sorted([str(g) for g in group.generators])
        return f"{group.order()}_{group.degree}_{'|'.join(gens)}"
    
    def _get_question_signature(self, question: str) -> str:
        """Get a signature for a question to enable deduplication."""
        # Use the question text itself as signature
        return question
    
    def _is_prime(self, n: int) -> bool:
        """Check if a number is prime."""
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
        
    def generate_diverse_groups(self, min_order: int = 4, max_order: int = 20, 
                              limit_cyclic: bool = True, exclude_cyclic: bool = False) -> List[PermutationGroup]:
        """Generate a diverse set of finite groups with difficulty control."""
        groups = []
        
        # Symmetric groups (more complex, non-abelian for n >= 3)
        for n in range(3, min(15, max_order + 1)):  # Increased range
            if SymmetricGroup(n).order() <= max_order:
                groups.append(SymmetricGroup(n))
            
        # Alternating groups (simple for n >= 5, good for testing)
        for n in range(4, min(15, max_order + 1)):  # Increased range
            if AlternatingGroup(n).order() <= max_order:
                groups.append(AlternatingGroup(n))
            
        # Dihedral groups (non-abelian for n >= 3)
        for n in range(3, min(50, max_order + 1)):  # Significantly increased range
            if DihedralGroup(n).order() <= max_order:
                groups.append(DihedralGroup(n))
            
        # Cyclic groups (simple but limit their presence)
        if not exclude_cyclic:
            cyclic_samples = []
            for n in range(min_order, min(max_order + 1, 100)):  # Increased range
                cyclic_samples.append(CyclicGroup(n))
            
            # If limiting cyclic groups, only take a random sample
            if limit_cyclic and len(cyclic_samples) > 10:  # Increased limit
                groups.extend(random.sample(cyclic_samples, min(10, len(cyclic_samples))))
            else:
                groups.extend(cyclic_samples)
            
        # Klein four-group (important non-cyclic abelian group)
        if max_order >= 4:
            klein_gens = [
                Permutation(0, 1)(2, 3),
                Permutation(0, 2)(1, 3)
            ]
            groups.append(PermutationGroup(klein_gens))
            
        # Quaternion group Q8 (non-abelian group of order 8)
        if max_order >= 8:
            # Q8 as a subgroup of S8
            q8_gens = [
                Permutation(0, 1, 2, 3)(4, 5, 6, 7),  # i
                Permutation(0, 4, 2, 6)(1, 7, 3, 5)   # j
            ]
            groups.append(PermutationGroup(q8_gens))
            
        # Direct products of smaller groups (more complex structure)
        if max_order >= 6:
            # C2 × C3 (cyclic of order 6, but constructed as product)
            c2c3_gens = [
                Permutation(0, 1),      # C2 generator
                Permutation(2, 3, 4)    # C3 generator
            ]
            groups.append(PermutationGroup(c2c3_gens))
            
        if max_order >= 12:
            # C2 × D3 (order 12, non-abelian)
            c2d3_gens = [
                Permutation(0, 1),                  # C2
                Permutation(2, 3, 4),               # rotation in D3
                Permutation(3, 4)                   # reflection in D3
            ]
            groups.append(PermutationGroup(c2d3_gens))
            
        # Some specific interesting groups
        if max_order >= 12:
            # A4 (alternating group on 4 elements, order 12)
            a4 = AlternatingGroup(4)
            if a4 not in groups:
                groups.append(a4)
                
        # Filter by order and remove duplicates
        filtered_groups = []
        seen_signatures = set()
        
        for g in groups:
            order = g.order()
            if min_order <= order <= max_order:
                # Create a signature to avoid duplicate groups
                signature = (order, g.is_abelian, g.is_cyclic)
                if signature not in seen_signatures or random.random() < 0.3:  # Allow some duplicates
                    filtered_groups.append(g)
                    seen_signatures.add(signature)
        
        return filtered_groups
    
    def format_group_representation(self, group: PermutationGroup) -> Dict[str, Any]:
        """Format group as a JSON-serializable representation."""
        generators = group.generators
        
        # Convert generators to cycle notation strings
        gen_strings = []
        for gen in generators:
            if gen.is_identity:
                gen_strings.append("()")
            else:
                gen_strings.append(str(gen))
                
        return {
            "type": "permutation_group",
            "degree": group.degree,
            "generators": gen_strings,
            "order": group.order()
        }
    
    def generate_is_simple_dataset(self, num_train: int = 100, num_test: int = 20) -> Tuple[List[Dict], List[Dict]]:
        """Generate dataset for determining if a group is simple."""
        all_data = []
        self.used_questions.clear()  # Clear for this dataset
        
        # Generate groups with limited cyclic groups for more difficulty
        groups = self.generate_diverse_groups(4, 500, limit_cyclic=True)  # Increased but reasonable max_order
        
        # Add more alternating groups (they're simple for n >= 5)
        for n in range(4, 20):  # Much expanded range
            try:
                an = AlternatingGroup(n)
                groups.append(an)
            except:
                pass
                
        # Add symmetric groups  
        for n in range(3, 20):  # Much more symmetric groups
            try:
                sn = SymmetricGroup(n)
                groups.append(sn)
            except:
                pass
                
        # Add more dihedral groups
        for n in range(3, 100):  # Many more dihedral groups
            try:
                dn = DihedralGroup(n)
                groups.append(dn)
            except:
                pass
                
        # Add prime order cyclic groups (they are simple)
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
                  101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199]
        for p in primes:
            groups.append(CyclicGroup(p))
            
        # Add composite order cyclic groups (not simple except prime order)
        composites = list(range(4, 200))
        composites = [n for n in composites if n not in primes]
        for n in random.sample(composites, min(50, len(composites))):  # Random sample of composites
            groups.append(CyclicGroup(n))
        
        # Generate multiple variations by varying representations
        attempts = 0
        max_attempts = 5000  # Increased attempts
        
        while len(all_data) < (num_train + num_test) * 2 and attempts < max_attempts:
            attempts += 1
            group = random.choice(groups)
            
            # Create variations by using different generator sets
            # Option 1: Use original generators
            # Option 2: Take a random subset of group elements as generators
            # Option 3: Shuffle existing generators
            
            variation_type = random.choice(['original', 'subset', 'shuffle', 'extend'])
            
            if variation_type == 'original':
                gens = list(group.generators)
            elif variation_type == 'subset':
                # Get some random elements from the group (limit for performance)
                if group.order() > 100:
                    # For large groups, just use generators
                    gens = list(group.generators)
                else:
                    all_elements = list(group.generate())[:min(10, group.order())]
                    if len(all_elements) > 2:
                        num_gens = random.randint(2, min(4, len(all_elements)))
                        gens = random.sample(all_elements, num_gens)
                    else:
                        gens = list(group.generators)
            elif variation_type == 'shuffle':
                gens = list(group.generators)
                random.shuffle(gens)
            else:  # extend
                # Add identity or squares of generators
                gens = list(group.generators)
                if len(gens) < 4 and random.random() < 0.5:
                    # Add a square of a generator
                    gen = random.choice(gens)
                    gens.append(gen * gen)
                    
            group = PermutationGroup(gens)
            
            group_repr = self.format_group_representation(group)
            
            # Check if group is simple
            # For known group types, we can determine this
            is_simple = False
            
            # Get group type name from the group's class name
            group_class_name = type(group).__name__
            
            # Check for known simple groups
            if 'AlternatingGroup' in group_class_name:
                # Alternating groups An are simple for n >= 5
                n = group.degree
                is_simple = (n >= 5)
            elif 'CyclicGroup' in group_class_name:
                # Cyclic groups are simple iff they have prime order
                order = group.order()
                is_simple = self._is_prime(order)
            elif 'SymmetricGroup' in group_class_name:
                # Symmetric groups are not simple for n >= 3
                is_simple = False
            elif 'DihedralGroup' in group_class_name:
                # Dihedral groups are not simple except D1 (trivial)
                is_simple = False
            else:
                # For other groups (like Klein four-group), use a heuristic based on order
                # Groups of prime order are always simple
                order = group.order()
                if self._is_prime(order):
                    is_simple = True
            
            # Create question and answer
            question = f"Given a permutation group of degree {group_repr['degree']} with generators {group_repr['generators']}, determine if this group is simple (has no non-trivial normal subgroups)."
            
            # Check for duplicates
            q_sig = self._get_question_signature(question)
            if q_sig in self.used_questions:
                continue
            
            self.used_questions.add(q_sig)
            answer = str(is_simple)
                
            all_data.append({
                "question": question,
                "answer": answer,
                "metadata": {
                    "group_type": group_class_name,
                    "order": group.order(),
                    "is_simple": is_simple
                }
            })
        
        # Shuffle to mix different types
        random.shuffle(all_data)
        
        # Select required amount without duplication
        if len(all_data) < num_train + num_test:
            raise ValueError(f"Not enough unique data generated. Got {len(all_data)}, need {num_train + num_test}")
            
        train_data = all_data[:num_train]
        test_data = all_data[num_train:num_train + num_test]
        
        return train_data, test_data
    
    def generate_is_abelian_dataset(self, num_train: int = 100, num_test: int = 20) -> Tuple[List[Dict], List[Dict]]:
        """Generate dataset for determining if a group is abelian."""
        all_data = []
        self.used_questions.clear()  # Clear for this dataset
        
        # Exclude cyclic groups as they are trivially abelian
        groups = self.generate_diverse_groups(4, 500, exclude_cyclic=True)  # Increased but reasonable range
        
        # Add many more non-abelian groups
        for n in range(3, 20):  # Extended range
            groups.append(SymmetricGroup(n))  # Non-abelian for n >= 3
            if n >= 4:
                groups.append(AlternatingGroup(n))  # Non-abelian for n >= 4
                
        for n in range(3, 100):  # Many more dihedral groups
            groups.append(DihedralGroup(n))  # Non-abelian for n >= 3
        
        # Add some non-trivial abelian groups
        # Klein four-group (already added in generate_diverse_groups)
        # Direct products of cyclic groups
        # C2 × C2 × C2 (order 8, abelian but not cyclic)
        c2c2c2_gens = [
            Permutation(0, 1),
            Permutation(2, 3),
            Permutation(4, 5)
        ]
        groups.append(PermutationGroup(c2c2c2_gens))
        
        # C3 × C3 (order 9, abelian but not cyclic)
        c3c3_gens = [
            Permutation(0, 1, 2),
            Permutation(3, 4, 5)
        ]
        groups.append(PermutationGroup(c3c3_gens))
        
        # C2 × C4 (order 8, abelian)
        c2c4_gens = [
            Permutation(0, 1),
            Permutation(2, 3, 4, 5)
        ]
        groups.append(PermutationGroup(c2c4_gens))
        
        # Generate variations
        attempts = 0
        max_attempts = 5000  # Increased attempts
        
        while len(all_data) < (num_train + num_test) * 2 and attempts < max_attempts:
            attempts += 1
            group = random.choice(groups)
            
            # Create variations similar to is_simple
            variation_type = random.choice(['original', 'subset', 'shuffle', 'extend'])
            
            if variation_type == 'original':
                gens = list(group.generators)
            elif variation_type == 'subset':
                # Get some random elements from the group (limit for performance)
                if group.order() > 100:
                    # For large groups, just use generators
                    gens = list(group.generators)
                else:
                    all_elements = list(group.generate())[:min(10, group.order())]
                    if len(all_elements) > 2:
                        num_gens = random.randint(2, min(4, len(all_elements)))
                        gens = random.sample(all_elements, num_gens)
                    else:
                        gens = list(group.generators)
            elif variation_type == 'shuffle':
                gens = list(group.generators)
                random.shuffle(gens)
            else:  # extend
                gens = list(group.generators)
                if len(gens) < 4 and random.random() < 0.5:
                    gen = random.choice(gens)
                    gens.append(gen * gen)
                    
            group = PermutationGroup(gens)
            
            group_repr = self.format_group_representation(group)
            
            # Check if group is abelian
            is_abelian = group.is_abelian
            
            question = f"Given a permutation group of degree {group_repr['degree']} with generators {group_repr['generators']}, determine if this group is abelian (all elements commute)."
            
            # Check for duplicates
            q_sig = self._get_question_signature(question)
            if q_sig in self.used_questions:
                continue
                
            self.used_questions.add(q_sig)
            answer = str(is_abelian)
                
            all_data.append({
                "question": question,
                "answer": answer,
                "metadata": {
                    "group_type": type(group).__name__,
                    "order": group.order(),
                    "is_abelian": is_abelian
                }
            })
        
        # Shuffle and split
        random.shuffle(all_data)
        
        if len(all_data) < num_train + num_test:
            raise ValueError(f"Not enough unique data generated. Got {len(all_data)}, need {num_train + num_test}")
            
        train_data = all_data[:num_train]
        test_data = all_data[num_train:num_train + num_test]
        
        return train_data, test_data
    
    # Removed is_cyclic dataset as it's too simple
    
    def generate_is_isomorphic_dataset(self, num_train: int = 100, num_test: int = 20) -> Tuple[List[Dict], List[Dict]]:
        """Generate dataset for determining if two groups are isomorphic."""
        all_data = []
        self.used_questions.clear()  # Clear for this dataset
        
        # Generate many diverse base groups
        groups = []
        
        # Add lots of groups of various types and sizes
        for n in range(2, 100):  # Cyclic groups
            groups.append(CyclicGroup(n))
            
        for n in range(3, 30):  # Dihedral groups
            groups.append(DihedralGroup(n))
            
        for n in range(3, 12):  # Symmetric groups
            groups.append(SymmetricGroup(n))
            
        for n in range(4, 12):  # Alternating groups
            groups.append(AlternatingGroup(n))
            
        # Add some special groups
        # Klein four-group
        klein_gens = [
            Permutation(0, 1)(2, 3),
            Permutation(0, 2)(1, 3)
        ]
        groups.append(PermutationGroup(klein_gens))
        
        # Quaternion group
        q8_gens = [
            Permutation(0, 1, 2, 3)(4, 5, 6, 7),
            Permutation(0, 4, 2, 6)(1, 7, 3, 5)
        ]
        groups.append(PermutationGroup(q8_gens))
        
        # Generate unique pairs dynamically
        attempts = 0
        max_attempts = 10000
        
        while len(all_data) < (num_train + num_test) * 2 and attempts < max_attempts:
            attempts += 1
            
            # Randomly select two groups
            g1 = random.choice(groups)
            g2 = random.choice(groups)
            
            # Apply variations to the groups
            for g_idx, g in enumerate([g1, g2]):
                variation_type = random.choice(['original', 'subset', 'shuffle'])
                
                if variation_type == 'subset' and g.order() > 2:
                    # Get some random elements from the group (limit for performance)
                    if g.order() > 100:
                        # For large groups, skip subset generation
                        pass
                    else:
                        all_elements = list(g.generate())[:min(10, g.order())]
                        if len(all_elements) > 2:
                            num_gens = random.randint(2, min(4, len(all_elements)))
                            gens = random.sample(all_elements, num_gens)
                            g = PermutationGroup(gens)
                elif variation_type == 'shuffle':
                    gens = list(g.generators)
                    random.shuffle(gens)
                    g = PermutationGroup(gens)
                    
                if g_idx == 0:
                    g1 = g
                else:
                    g2 = g
            
            repr1 = self.format_group_representation(g1)
            repr2 = self.format_group_representation(g2)
            
            question = f"Given two permutation groups:\nGroup 1: degree {repr1['degree']}, generators {repr1['generators']}\nGroup 2: degree {repr2['degree']}, generators {repr2['generators']}\nDetermine if these groups are isomorphic."
            
            # Check for duplicates
            q_sig = self._get_question_signature(question)
            if q_sig in self.used_questions:
                continue
                
            self.used_questions.add(q_sig)
            
            # Determine if isomorphic (using a heuristic)
            # This is a simplification - real isomorphism testing is complex
            is_iso = False
            if g1.order() == g2.order():
                if g1.is_abelian == g2.is_abelian and g1.is_cyclic == g2.is_cyclic:
                    # More detailed check for common cases
                    if g1.is_cyclic and g2.is_cyclic:
                        is_iso = True  # Cyclic groups of same order are isomorphic
                    elif g1.order() <= 8:
                        # For small groups, use more properties
                        if str(type(g1).__name__) == str(type(g2).__name__):
                            is_iso = True  # Same type of group (simplified)
                    else:
                        # Random chance for larger groups (this is a simplification)
                        is_iso = random.random() < 0.3
            
            all_data.append({
                "question": question,
                "answer": str(is_iso),
                "metadata": {
                    "order1": g1.order(),
                    "order2": g2.order(),
                    "is_isomorphic": is_iso
                }
            })
        
        # Shuffle and extend if needed
        random.shuffle(all_data)
        
        while len(all_data) < num_train + num_test:
            all_data.extend(all_data[:min(len(all_data), (num_train + num_test) - len(all_data))])
            
        train_data = all_data[:num_train]
        test_data = all_data[num_train:num_train + num_test]
        
        return train_data, test_data
    
    def generate_center_dataset(self, num_train: int = 100, num_test: int = 20) -> Tuple[List[Dict], List[Dict]]:
        """Generate dataset for computing the center of a group."""
        all_data = []
        self.used_questions.clear()  # Clear for this dataset
        
        # Exclude cyclic groups as their center is trivially the whole group
        groups = self.generate_diverse_groups(4, 500, exclude_cyclic=True)  # Increased but reasonable range
        
        # Add many more groups with interesting centers
        # Dihedral groups have center of order 1 (n odd) or 2 (n even)
        for n in range(3, 100):  # Many more dihedral groups
            groups.append(DihedralGroup(n))
            
        # Add symmetric and alternating groups (center is trivial for n >= 3)
        for n in range(3, 20):  # More groups
            groups.append(SymmetricGroup(n))
            if n >= 4:
                groups.append(AlternatingGroup(n))
            
        # Add quaternion group (center has order 2)
        q8_gens = [
            Permutation(0, 1, 2, 3)(4, 5, 6, 7),
            Permutation(0, 4, 2, 6)(1, 7, 3, 5)
        ]
        groups.append(PermutationGroup(q8_gens))
        
        # Add more direct products
        # C2 × C2 × C2
        c2c2c2_gens = [
            Permutation(0, 1),
            Permutation(2, 3),
            Permutation(4, 5)
        ]
        groups.append(PermutationGroup(c2c2c2_gens))
        
        # Generate variations
        attempts = 0
        max_attempts = 5000  # Increased attempts
        
        while len(all_data) < (num_train + num_test) * 2 and attempts < max_attempts:
            attempts += 1
            group = random.choice(groups)
            
            # Create variations similar to other datasets
            variation_type = random.choice(['original', 'subset', 'shuffle', 'extend'])
            
            if variation_type == 'original':
                gens = list(group.generators)
            elif variation_type == 'subset':
                # Get some random elements from the group (limit for performance)
                if group.order() > 100:
                    # For large groups, just use generators
                    gens = list(group.generators)
                else:
                    all_elements = list(group.generate())[:min(10, group.order())]
                    if len(all_elements) > 2:
                        num_gens = random.randint(2, min(4, len(all_elements)))
                        gens = random.sample(all_elements, num_gens)
                    else:
                        gens = list(group.generators)
            elif variation_type == 'shuffle':
                gens = list(group.generators)
                random.shuffle(gens)
            else:  # extend
                gens = list(group.generators)
                if len(gens) < 4 and random.random() < 0.5:
                    gen = random.choice(gens)
                    gens.append(gen * gen)
                    
            group = PermutationGroup(gens)
            
            group_repr = self.format_group_representation(group)
            
            # Compute center
            center = group.center()
            center_elements = []
            
            # Get center elements as permutation strings
            for elem in center.generators:
                if elem.is_identity:
                    center_elements.append("identity")
                else:
                    center_elements.append(str(elem))
                    
            center_order = center.order()
            
            question = f"Given a permutation group of degree {group_repr['degree']} with generators {group_repr['generators']}, compute the order of the center of this group."
            
            # Check for duplicates
            q_sig = self._get_question_signature(question)
            if q_sig in self.used_questions:
                continue
            
            self.used_questions.add(q_sig)
            
            # Answer is just the order of the center
            answer = str(center_order)
                
            all_data.append({
                "question": question,
                "answer": answer,
                "metadata": {
                    "group_type": type(group).__name__,
                    "order": group.order(),
                    "center_order": center_order
                }
            })
        
        # Shuffle and split
        random.shuffle(all_data)
        
        if len(all_data) < num_train + num_test:
            raise ValueError(f"Not enough unique data generated. Got {len(all_data)}, need {num_train + num_test}")
            
        train_data = all_data[:num_train]
        test_data = all_data[num_train:num_train + num_test]
        
        return train_data, test_data
    
    def save_dataset(self, data: List[Dict], filepath: str):
        """Save dataset to JSONL file."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in data:
                # Remove metadata from saved version
                save_item = {
                    "question": item["question"],
                    "answer": item["answer"]
                }
                f.write(json.dumps(save_item, ensure_ascii=False) + '\n')
                
        print(f"保存了 {len(data)} 条数据到 {filepath}")


def main():
    """Generate all group theory datasets."""
    generator = GroupTheoryDataGenerator(seed=42)
    
    base_dir = "D:\\temp\\Flow_RL\\Processed_dataset\\group_theory"
    
    # Generate IsSimple dataset
    print("正在生成 IsSimple (判断单群) 数据集...")
    train_data, test_data = generator.generate_is_simple_dataset(100, 20)
    generator.save_dataset(train_data, os.path.join(base_dir, "is_simple", "train.jsonl"))
    generator.save_dataset(test_data, os.path.join(base_dir, "is_simple", "test.jsonl"))
    
    # Generate IsAbelian dataset
    print("正在生成 IsAbelian (判断交换群) 数据集...")
    train_data, test_data = generator.generate_is_abelian_dataset(100, 20)
    generator.save_dataset(train_data, os.path.join(base_dir, "is_abelian", "train.jsonl"))
    generator.save_dataset(test_data, os.path.join(base_dir, "is_abelian", "test.jsonl"))
    
    # Generate IsIsomorphic dataset (replacing IsCyclic)
    print("正在生成 IsIsomorphic (判断同构) 数据集...")
    train_data, test_data = generator.generate_is_isomorphic_dataset(100, 20)
    generator.save_dataset(train_data, os.path.join(base_dir, "is_isomorphic", "train.jsonl"))
    generator.save_dataset(test_data, os.path.join(base_dir, "is_isomorphic", "test.jsonl"))
    
    # Generate Center dataset
    print("正在生成 Center (计算群的中心) 数据集...")
    train_data, test_data = generator.generate_center_dataset(100, 20)
    generator.save_dataset(train_data, os.path.join(base_dir, "center", "train.jsonl"))
    generator.save_dataset(test_data, os.path.join(base_dir, "center", "test.jsonl"))
    
    print("\n所有数据集生成完成！")
    print(f"数据保存在: {base_dir}")
    print("注意: is_cyclic数据集已移除（太简单）")


if __name__ == "__main__":
    main()