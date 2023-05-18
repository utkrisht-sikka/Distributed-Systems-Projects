
ALLOWED_TYPES = ["SPORTS", "FASHION", "POLITICS"]

class Article:
    
    def __init__(self, type, author, content, time, client_id, server_address):
        self.type = type
        self.author = author
        self.content = content
        self.time = time
        self.submitted_client = client_id
        self.submitted_server = server_address
    
    def __str__(self):
        return f"Article : [{self.type}, {self.author}, {self.content}, {self.time}]"
    
    
    @staticmethod
    def filter_by_type(articles, type_tag):
        
        if(type_tag == 4):
            return articles
        
        filtered_list = []
        for article in articles:
            if(article.type == type_tag):
                filtered_list.append(article)
        return filtered_list
    
    @staticmethod
    def filter_by_author(articles, author_tag):
        
        if(author_tag == '<blank>'):
            return articles
        
        filtered_list = []
        for article in articles:
            if(article.author == author_tag):
                filtered_list.append(article)
        return filtered_list
    
    @staticmethod
    def filter_by_date(articles, time_tag):
        
        filtered_list = []
        for article in articles:
            if(article.time.seconds > time_tag.seconds):
                filtered_list.append(article)
            elif(article.time.seconds == time_tag.seconds):
                if(article.time.nanos >= time_tag.nanos):
                    filtered_list.append(article)
                
        return filtered_list