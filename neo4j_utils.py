from neo4j import GraphDatabase

class Neo4jUtils:
    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "Ian910504"))

    def test_connection(self):
        """Test if the connection works and print database info"""
        try:
            with self.driver.session(database="academicworld") as session:
                # Test connection
                result = session.run("RETURN 'Connected to Neo4j' AS message")
                record = result.single()
                print(f"✅ {record['message']}")
                
                # Show available labels
                result = session.run("CALL db.labels()")
                labels = [record["label"] for record in result]
                print(f"Available node labels: {labels}")
                
                # Show available relationships
                result = session.run("CALL db.relationshipTypes()")
                rels = [record["relationshipType"] for record in result]
                print(f"Available relationships: {rels}")
                
                return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def get_sample_faculty_names(self, limit=5):
        """Get some faculty names to test with"""
        queries = [
            "MATCH (f:FACULTY) RETURN f.name AS name LIMIT $limit",
            "MATCH (f:Faculty) RETURN f.name AS name LIMIT $limit", 
            "MATCH (f) WHERE 'FACULTY' IN labels(f) RETURN f.name AS name LIMIT $limit",
            "MATCH (f) WHERE any(label IN labels(f) WHERE toLower(label) CONTAINS 'faculty') RETURN f.name AS name LIMIT $limit"
        ]
        
        with self.driver.session(database="academicworld") as session:
            for query in queries:
                try:
                    result = session.run(query, limit=limit)
                    names = [record["name"] for record in result if record["name"]]
                    if names:
                        print(f"Found faculty names: {names}")
                        return names
                except Exception as e:
                    continue
            
            print("❌ No faculty found. Check your data loading.")
            return []

    def get_top_publications(self, faculty_name):
        """Get top publications for a faculty member"""
        queries = [
            # Standard query
            """
            MATCH (f:FACULTY {name: $name})-[:PUBLISH]->(p:PUBLICATION)
            RETURN p.id AS id, p.title AS title, p.numCitations AS cites
            ORDER BY cites DESC LIMIT 5
            """,
            
            # Case insensitive exact match
            """
            MATCH (f:FACULTY)-[:PUBLISH]->(p:PUBLICATION)
            WHERE toLower(f.name) = toLower($name)
            RETURN p.id AS id, p.title AS title, p.numCitations AS cites
            ORDER BY cites DESC LIMIT 5
            """,
            
            # Partial name match
            """
            MATCH (f:FACULTY)-[:PUBLISH]->(p:PUBLICATION)
            WHERE toLower(f.name) CONTAINS toLower($name)
            RETURN p.id AS id, p.title AS title, p.numCitations AS cites
            ORDER BY cites DESC LIMIT 5
            """,
            
            # Try different relationship name
            """
            MATCH (f:FACULTY {name: $name})-[:AUTHORED]->(p:PUBLICATION)
            RETURN p.id AS id, p.title AS title, p.numCitations AS cites
            ORDER BY cites DESC LIMIT 5
            """,
            
            # Try with Faculty label (capital F)
            """
            MATCH (f:Faculty {name: $name})-[:PUBLISH]->(p:PUBLICATION)
            RETURN p.id AS id, p.title AS title, p.numCitations AS cites
            ORDER BY cites DESC LIMIT 5
            """
        ]
        
        with self.driver.session(database="academicworld") as session:
            for i, query in enumerate(queries):
                try:
                    result = session.run(query, name=faculty_name)
                    records = [record.data() for record in result]
                    if records:
                        print(f"✅ Query {i+1} succeeded, these are top {len(records)} publications")
                        return records
                except Exception as e:
                    print(f"❌ Query {i+1} failed: {e}")
                    continue
            
            print(f"❌ No publications found for '{faculty_name}'")
            return []

    def get_keywords_for_publication(self, pub_id):
        """Get keywords for a specific publication"""
        queries = [
            # Standard query
            """
            MATCH (p:PUBLICATION {id: $pid})-[r:LABEL_BY]->(k:KEYWORD)
            RETURN k.name AS kw, r.score AS score
            ORDER BY score DESC LIMIT 3
            """,
            
            # Try different relationship names
            """
            MATCH (p:PUBLICATION {id: $pid})-[r]->(k:KEYWORD)
            WHERE type(r) IN ['LABEL_BY', 'TAGGED_BY', 'HAS_KEYWORD']
            RETURN k.name AS kw, 
                   CASE WHEN r.score IS NOT NULL THEN r.score ELSE 1.0 END AS score
            ORDER BY score DESC LIMIT 3
            """,
            
            # Generic keyword relationship
            """
            MATCH (p:PUBLICATION {id: $pid})-[r]->(k:KEYWORD)
            RETURN k.name AS kw, 
                   CASE WHEN r.score IS NOT NULL THEN r.score 
                        WHEN r.weight IS NOT NULL THEN r.weight 
                        ELSE 1.0 END AS score
            ORDER BY score DESC LIMIT 3
            """,
            
            # Try with Keyword label (capital K)
            """
            MATCH (p:PUBLICATION {id: $pid})-[r:LABEL_BY]->(k:Keyword)
            RETURN k.name AS kw, r.score AS score
            ORDER BY score DESC LIMIT 3
            """
        ]
        
        with self.driver.session(database="academicworld") as session:
            for i, query in enumerate(queries):
                try:
                    result = session.run(query, pid=pub_id)
                    records = [record.data() for record in result]
                    if records:
                        print(f"✅ Keyword query {i+1} succeeded, found {len(records)} keywords")
                        return records
                except Exception as e:
                    print(f"❌ Keyword query {i+1} failed: {e}")
                    continue
            
            print(f"❌ No keywords found for publication {pub_id}")
            return []

    def debug_faculty_structure(self, faculty_name):
        """Debug what properties and relationships a faculty has"""
        query = """
        MATCH (f:FACULTY)
        WHERE toLower(f.name) CONTAINS toLower($name)
        OPTIONAL MATCH (f)-[r]->(connected)
        RETURN f.name AS faculty_name, 
               keys(f) AS faculty_properties,
               collect(DISTINCT type(r)) AS relationships,
               collect(DISTINCT labels(connected)[0]) AS connected_to
        LIMIT 1
        """
        
        with self.driver.session(database="academicworld") as session:
            try:
                result = session.run(query, name=faculty_name)
                record = result.single()
                if record:
                    print(f"Faculty: {record['faculty_name']}")
                    print(f"Properties: {record['faculty_properties']}")
                    print(f"Relationships: {record['relationships']}")
                    print(f"Connected to: {record['connected_to']}")
                    return record.data()
                else:
                    print(f"No faculty found matching '{faculty_name}'")
                    return None
            except Exception as e:
                print(f"Debug query failed: {e}")
                return None

    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()
