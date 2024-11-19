def message_clients_helper(driver):
    while True:
        print('in the message clients function now')
        matchedListings = matchedListingsTable.scan()
        #print("matched_listings: ", matchedListings)
        driver.implicitly_wait(20)
        try:
            for item in matchedListings['Items']:
                URL = item['listing_url']
                price = item['price']
                title = item['title']


            # URL = "https://www.facebook.com/marketplace/item/2470984673292700/?ref=browse_tab&referral_code=marketplace_top_picks&referral_story_type=top_picks"

            
            
                driver.get(URL)

                with open(cookies_file, mode='r') as file:
                    csv_reader = csv.DictReader(file)
                    for row in csv_reader:
                        cookie = {
                            'name': row['\ufeffname'],
                            'value': row['value'],
                            'domain': row['domain']
                        }
                        driver.add_cookie(cookie)
                driver.refresh()
                print("cookies added successfully")



                soup = BeautifulSoup(driver.page_source, 'html5lib') 
                links = soup.findAll('a', attrs={'class': 'x972fbf'})
                profile_links = [i.get('href') for i in links if 'profile' in i.get('href')]
                profile_id = profile_links[0].split('/')[3]
                messenger_link = "https://www.facebook.com/messages/t/" + profile_id

                #put profile_id in the driver.get below
                #messenger_link = "https://www.facebook.com/messages/t/100014276325191"
                #me = "https://www.facebook.com/messages/t/100014276325191"
                #steven = https://www.facebook.com/messages/t/100008157428607
                driver.get(messenger_link)

                time.sleep (10)
                texts = all_ongoing_texts_with_client(driver)
                """
                after this:
                    keep track of the last sent or received message, 
                    check if there's a change in the messages list
                    if yes, it means client messaged so you should send a message back
                    if no, client has not messaged back so no need to send a message
                """
                theElement = driver.find_element(By.XPATH, '//div[@aria-label="Message"]')
                #print("texts from message_helper: ", texts)
                # if it's the first contact
                if len(texts) == 0:
                    messages = [
                        f"Hello, I hope you’re having a good day. Just saw that you're selling {title}  on marketplace {URL}. I can come pick this up and pay you ${price} in cash.",
                        f"Hello, just saw that you're selling a {title}  on marketplace {URL}. I can pay you ${price} in cash and come pick it up.",
                        f"Hey, just saw that you're selling a {title} on marketplace {URL}. I can come pick this up and pay you ${price} in cash.",
                        f"Hi, just saw that you're selling {title}  on marketplace {URL}. I could pay you up to ${price} in cash and I could come pick it up.",
                        f"Hi, just saw that you're selling {title}  on marketplace {URL}. I can come pick this phone up for ${price} in cash asap. Where are you located?",
                        f"Just saw that you're selling {title}  on marketplace {URL}. Can I please come pickup for ${price}?",
                        f"Just saw that you're selling {title}  on marketplace {URL}. I can pickup for ${price}in cash.",
                        f"Just saw that you're selling {title}  on marketplace {URL}. Would you do ${price} in cash?",
                        f"Just saw that you're selling {title}  on marketplace {URL}. I can pay the full ${price} in cash. What's a good meetup spot for you?",
                        f"Just saw that you're selling {title}  on marketplace {URL}. Let's do the ${price} in cash. Where are you located?"

                    ]
                    message = random.choice(messages)
                    try:
                        theElement.click()
                        recent_message = ""
                        print("about to send first message")
                        for i in message:
                            recent_message += i
                            theElement.send_keys(i)
                        #send the first message
                        theElement.send_keys(Keys.RETURN)
                        print("first message is: ", message)
                        #save the first message to the MessagesData DB
                        #driver.implicitly_wait(20)
                        """
                        messagesTable.put_item(
                            Item= {
                                'messenger_link': messenger_link,
                                'product_url': URL,
                                'recent_message': message
                            },

                        )
                        """
                        #INSERT MESSAGE IN DB
                        try:
                            messagesTable.update_item(
                            Key={'product_url': URL},
                            UpdateExpression="""
                                SET
                                    messenger_link = :messenger_link,
                                    product_url = :product_url,
                                    recent_message = :recent_message  
                            """,
                            ExpressionAttributeValues={
                                ':messenger_link': messenger_link,
                                ':product_url': URL,
                                ':recent_message': recent_message
                            },
                            ReturnValues="ALL_NEW"
                        )
                        except Exception as e:
                            print("could not insert first message in DB: ", str(e))
                        



                        SENDER_EMAIL = os.getenv("SENDER_EMAIL")
                        SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
                        RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
                        
                        SUBJECT = "🟢 STARTED A CONVERSATION"
                        BODY = f"Just started chatting with a client. View our conversation here: {messenger_link}"

                        send_email(SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL, SUBJECT, BODY)
                                    
                        print("sent and saved first message")
                    except Exception as e:
                        print("Error sending first message: ", str(e))

                #if we're replying to the client
                elif len(texts) > 0:
                    recent_message = ""
                    payload = messagesTable.get_item(
                        Key={'product_url': URL},
                        ProjectionExpression='recent_message'
                    )
                    print("about to check if item not in payload")
                    if 'Item' not in payload:
                        """
                        messagesTable.put_item(
                                    Item={
                                        'messenger_link': messenger_link,
                                        'product_url': URL,
                                        'recent_message': ""
                                    },

                        )
                        """
                        try:
                            messagesTable.update_item(
                            Key={'product_url': URL},
                            UpdateExpression="""
                                SET
                                    messenger_link = :messenger_link,
                                    recent_message = :recent_message  
                            """,
                            ExpressionAttributeValues={
                                ':messenger_link': messenger_link,
                                ':recent_message': recent_message
                            },
                            ReturnValues="ALL_NEW"
                        )
                        except Exception as e:
                            print("could not insert first message in DB: ", str(e))
                        
                    
                    
                    currentChat = messagesTable.get_item(Key={'product_url': URL})


                    #get the most recent message sent
                    
                    recent_message = currentChat['Item']['recent_message']
                    #if the most recent message is not the same as the message in the messaging area, we have a response
                    if texts[-1] != recent_message:
                        #get the response from the AI bot and send it
                        message = get_response(texts[-1], messenger_link)
                        #print("message is: ", message)
                        #print("texts[-1]: ", texts[-1])
                        recent_message = message

                        if message != None or message != '':
                            for i in message:
                                theElement.send_keys(i)
                            theElement.send_keys(Keys.RETURN)
                            print("message sent")
                            #driver.implicitly_wait(20)

    


                        #now update the recent message of that chat
                        #if we can find the current chat item in the DB, we update the most recent message

                        if len(currentChat['Item']) == 1:
                            messagesTable.update_item(
                                Key={'product_url': URL},
                                UpdateExpression='SET recent_message = :val',
                                ExpressionAttributeValues={':val': recent_message}
                            )
                            print("updated the message in the DB")
                            check_convo_end(texts[-1], temp, messenger_link)

                        #else we create a new chat in the DB 
                        else:
                            messagesTable.put_item(
                                Item={
                                    'messenger_link': messenger_link,
                                    'product_url': URL,
                                    'recent_message': recent_message
                                },

                
                            )
                #here
            time.sleep(5 * 60)
                
        except Exception as e:
            
            print("error: ", str(e))




