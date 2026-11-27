# Master Chef's RAG

<p class="project-meta">Personal projects · 2026-11</p>

<span class="tag">Python</span> <span class="tag">FastAPI</span> <span class="tag">React</span> <span class="tag">BM25</span> <span class="tag">bge-small</span> <span class="tag">Qwen2.5</span> <span class="tag">RAG</span> <span class="tag">LLM</span> <span class="tag">information retrieval</span> <span class="tag">evaluation</span>

!!! note ""
    The source code is private; get in touch to request access.

Ask for a recipe in plain English, with constraints if you like ("vegetarian pasta with mushrooms in under
30 minutes"), and get an answer that cites the recipes it used, or a clear "nothing matches" when nothing does.

## See it in action

<video class="demo-video" src="media/demo.webm" autoplay loop muted playsinline controls></video>

Three questions on the web interface: a constrained search, a dietary request and an off-topic question it declines.

## Prepared questions

Real outputs of the full system (hybrid search, filters and a 7B model running locally on a GPU), recorded on
17 prepared questions. Open any of them to see the filters it understood, the answer, and the facts of the recipes
it retrieved.

<details class="replay" markdown>
<summary><b>Vegetarian pasta with mushrooms in under 30 minutes</b> <span class="tag">answered</span> <span class="tag">1.6 s</span></summary>

**Filters understood:** ready in 30 min or less, vegetarian, contains mushrooms

**Answer:**

> Here are a few vegetarian pasta recipes with mushrooms ready in under 30 minutes:
>
> - Blue Cheese and Mushroom Pasta: A quick and easy pasta dish with a blend of mushrooms and creamy blue cheese.
> - Cheesy Shells and Green Beans: While not a traditional pasta dish, this recipe combines pasta shells with mushrooms, cheese, and green beans for a quick vegetarian meal.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | Blue cheese and mushroom pasta | 25 min | 242 | onion, garlic, mushrooms, blue cheese, yoghurt, creme fraiche … |
| ✓ cited | Cheesy shells and green beans | 22 min | 20 | velveeta shells and cheese dinner, frozen cut green beans, mushrooms, french-fried onions |
|  | Bulgur with crimini mushrooms | 25 min | 172 | extra virgin olive oil, garlic cloves, onion, mushrooms, mushroom stock, bulgur … |
|  | Broiled polenta with mushrooms and cheese | 30 min | 186 | boiling water, dried porcini mushrooms, water, salt, cornmeal, olive oil … |
|  | Cannellini piccata | 20 min | 463 | olive oil, onion, garlic clove, white mushroom, flour, vegetable broth … |

</details>

<details class="replay" markdown>
<summary><b>A gluten-free dessert a child would like</b> <span class="tag">answered</span> <span class="tag">1.1 s</span></summary>

**Filters understood:** gluten-free

**Answer:**

> The always tastes great gluten-free easy cake with variations would be a delightful choice for a child. It's kid-friendly, easy to prepare, and comes with variations to keep things interesting. Betty Erlich's potato cake gluten free is another option, being both simple and using familiar ingredients like potatoes and eggs, which might appeal to children.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | Always tastes great gluten free easy cake with variations | 40 min | 209 | gluten-free self-raising flour, butter, sugar, gluten-free cornflour, gluten free baking powder, vanilla essence … |
| ✓ cited | Betty erlich s potato cake gluten free | 100 min | 169 | potatoes, eggs, caster sugar, ground almonds, lemon |
|  | Bread and butter pudding gluten free | 50 min | 325 | bread, butter, eggs, caster sugar, milk, cream … |
|  | Awesome gluten free chocolate chip cookies | 70 min | 915 | butter, brown sugar, sugar, vanilla instant pudding mix, eggs, vanilla extract … |
|  | Amazing gluten free buttermilk donuts doughnuts | 40 min | 120 | eggs, buttermilk, butter, gluten-free rice flour mix, sugar, nutmeg … |

</details>

<details class="replay" markdown>
<summary><b>Something with flour, milk and tomatoes</b> <span class="tag">answered</span> <span class="tag">1.1 s</span></summary>

**Filters understood:** contains flour, contains milk, contains tomatoes

**Answer:**

> Batter fried fresh tomatoes uses flour, milk, and tomatoes. It takes 20 minutes to prepare and is a low-calorie side dish. artichoke tomato and asiago focaccia also includes flour and milk, though it has a longer preparation time of 270 minutes.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | Batter fried fresh tomatoes | 20 min | 81 | flour, baking powder, salt, egg, milk, tomatoes … |
|  | Bush tomato damper | 60 min | 284 | all-purpose flour, baking powder, salt, sugar, unsalted butter, milk … |
|  | Cheese tomato bread | 75 min | 2311 | whole wheat flour, baking powder, baking soda, salt, garlic powder, oregano … |
| ✓ cited | Artichoke tomato and asiago focaccia | 270 min | 250 | all-purpose flour, milk, fast rising yeast, olive oil, salt, artichoke heart … |
|  | Baked chicken stuffed tomatoes | 30 min | 238 | tomatoes, butter, all-purpose flour, milk, chicken, celery … |

</details>

<details class="replay" markdown>
<summary><b>The quickest recipe with eggs, flour and milk</b> <span class="tag">answered</span> <span class="tag">601 ms</span></summary>

**Filters understood:** contains eggs, contains flour, contains milk

**Answer:**

> The quickest recipe with eggs, flour, and milk is anytime crepes, which takes 8 minutes to prepare.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | Anytime crepes | 8 min | 150 | egg, milk, whole wheat flour |
|  | Apple cinnamon pancakes | 15 min | 399 | flour, whole wheat flour, baking powder, cinnamon, milk, eggs … |
|  | Best ever low fat custard ice cream | 15 min | 467 | fat-free sweetened condensed milk, fat-free evaporated milk, eggs, sugar, flour, salt … |
|  | Make it your way shortcakes | 25 min | 175 | flour, salt, baking powder, sugar, butter, egg … |
|  | Chicken fried steak with gravy | 29 min | 439 | oil, beef cutlets, seasoned flour, eggs, milk, flour … |

</details>

<details class="replay" markdown>
<summary><b>A vegan soup with lentils</b> <span class="tag">answered</span> <span class="tag">1.8 s</span></summary>

**Filters understood:** vegan, contains lentils

**Answer:**

> Here are a few vegan soups with lentils from the provided recipes:
>
> - Bulgarian lentil soup: A 60-minute soup with brown lentils, onions, garlic, and a mix of spices.
> - Butternut squash and lentil soup: A 75-minute soup featuring butternut squash, lentils, and a blend of vegetables.
> - Cauliflower red lentil ginger soup: A 35-minute soup with a spicy twist, using cauliflower, red lentils, and ginger.
> - Attempting to duplicate progresso lentil soup: A 90-minute soup with a simpler ingredient list, including lentils, vegetable stock, and spinach.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | Bulgarian lentil soup | 60 min | 156 | brown lentils, onions, garlic, carrots, paprika, tomatoes … |
| ✓ cited | Butternut squash and lentil soup | 75 min | 82 | olive oil, onion, garlic cloves, carrot, celery, vegetable broth … |
|  | Brown lentil and vegetable soup | 35 min | 460 | olive oil, carrots, zucchini, celery, brown onion, diced tomatoes … |
| ✓ cited | Cauliflower red lentil ginger soup | 35 min | 171 | onion, fresh ginger, olive oil, garlic cloves, cumin seed, red pepper flakes … |
| ✓ cited | Attempting to duplicate progresso lentil soup | 90 min | 73 | celery, salt, garlic cloves, fresh ginger, fresh ground black pepper, lentils … |

</details>

<details class="replay" markdown>
<summary><b>Low-calorie chicken dinner under 400 calories</b> <span class="tag">answered</span> <span class="tag">1.4 s</span></summary>

**Filters understood:** under 400 kcal, low-calorie, contains chicken

**Answer:**

> 250 calorie dinner: This dish contains 233 kcal per serving and includes chicken breast, sliced mushrooms, fat-free Italian salad dressing, onion, low-fat margarine, zucchini, and tomatoes. It's a main dish that can be prepared in 65 minutes. chicken mashed potatoes: With 306 kcal per serving, this recipe is a quick and easy option, taking only 30 minutes to prepare. It uses potatoes, low sodium chicken broth, and garlic powder.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | 250 calorie dinner | 65 min | 233 | chicken breast, sliced mushrooms, fat-free italian salad dressing, onion, lowfat margarine, zucchini … |
| ✓ cited | Chicken mashed potatoes | 30 min | 306 | potatoes, low sodium chicken broth, garlic powder |
|  | Chicken dinner pot pie | 70 min | 208 | pastry for a double-crust 9-inch pie, butter, flour, salt, pepper, ground thyme … |
|  | 20 minute garlic rosemary chicken brown rice dinner | 60 min | 202 | oil, boneless skinless chicken breast halves, garlic powder, dried rosemary leaves, reduced-sodium chicken broth, water … |
|  | Chicken with sun dried tomatoes and artichokes 8 net carbs | 485 min | 348 | cooking spray, artichoke hearts, sun-dried tomato, cauliflower floret, garlic, dried oregano … |

</details>

<details class="replay" markdown>
<summary><b>A spicy Thai curry with coconut milk</b> <span class="tag">answered</span> <span class="tag">923 ms</span></summary>

**Filters understood:** contains coconut milk

**Answer:**

> The recipe that fits your description is awesome thai chicken coconut curry. This dish is a spicy Thai curry with coconut milk, taking 35 minutes to prepare and offering a protein content of 5% DV per serving. The ingredients include garlic, red curry paste, coconut milk, chicken breasts, and pineapple chunks.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | Awesome thai chicken coconut curry | 35 min | 318 | garlic clove, vegetable oil, fresh ginger, red curry paste, coconut milk, water … |
|  | Chicken floating in curried coconut soup | 60 min | 1040 | sesame oil, chicken breasts, coconut milk, chicken stock, lemongrass, kaffir lime leaves … |
|  | Chicken in red curry and coconut | 30 min | 512 | peanut oil, garlic cloves, whole chicken breasts, yellow onion, coconut milk, thai red curry paste … |
|  | Authentic thai red curry with chicken | 30 min | 1100 | boneless skinless chicken breasts, thai red curry paste, coconut milk, oil, chicken stock, chicken bouillon cube … |
|  | Broiled tilapia with thai coconut curry sauce | 30 min | 374 | dark sesame oil, fresh ginger, garlic cloves, red bell pepper, green onion, curry powder … |

</details>

<details class="replay" markdown>
<summary><b>Breakfast I can make in 10 minutes</b> <span class="tag">answered</span> <span class="tag">1.7 s</span></summary>

**Filters understood:** ready in 10 min or less

**Answer:**

> Here are some breakfast options you can make in 10 minutes or less:
>
> - 1 minute breakfast sandwich: A quick and satisfying meal with egg, cheese, bacon, and other toppings.
> - Breakfast salad: A light and healthy choice with yogurt, granola, fruits, and honey.
> - Breakfast parfait: A sweet and nutritious option with yogurt, oats, strawberries, walnuts, and frozen fruit.
> - Breakfast wrap: A hearty wrap with tortilla, cheese, egg, bacon, and spinach.
> - Breakfast delight rounds: Sweet and simple rounds made with english muffins, brown sugar, and apples.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | 1 minute breakfast sandwich | 3 min | 399 | egg, milk, salt, pepper, cooking spray, english muffin … |
| ✓ cited | Breakfast salad | 3 min | 140 | yogurt, granola cereal, blueberries, strawberry, banana, honey |
| ✓ cited | Breakfast parfait | 5 min | 414 | plain yogurt, rolled oats, strawberries, walnuts, honey, frozen fruit |
| ✓ cited | Breakfast wrap | 9 min | 515 | flour tortilla, mozzarella cheese, egg, bacon, frozen chopped spinach, ready-made bruschetta |
| ✓ cited | Breakfast delight rounds | 7 min | 315 | english muffins, brown sugar, butter, cinnamon, peanut butter, gala apples |

</details>

<details class="replay" markdown>
<summary><b>Dairy-free chocolate cake</b> <span class="tag">answered</span> <span class="tag">1.0 s</span></summary>

**Filters understood:** no milk, no butter, no cheese, no cream, no yogurt

**Answer:**

> The recipe for a dairy-free chocolate cake fits your request. It takes 50 minutes to prepare and has a high calorie count per serving. The ingredients include vegan margarine, sugar, eggs, vanilla, flour, cocoa powder, baking soda, salt, baking powder, and water.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | Chocolate cake dairy free | 50 min | 2552 | vegan margarine, sugar, eggs, vanilla, flour, cocoa powder … |
|  | Chocolate cake no milk required | 35 min | 248 | flour, sugar, cocoa, salt, baking soda, vinegar … |
|  | Chocolate cake | 45 min | 185 | sugar, flour, salt, baking soda, cocoa, miracle whip … |
|  | Chocolate cake with coconut topping vegan | 35 min | 5389 | all-purpose flour, unsweetened cocoa powder, baking soda, salt, guar gum, raw sugar … |
|  | Chocolate cake no eggs or butter | 70 min | 4429 | flour, sugar, salt, baking soda, cocoa, vanilla essence … |

</details>

<details class="replay" markdown>
<summary><b>A slow-cooker beef stew</b> <span class="tag">answered</span> <span class="tag">2.3 s</span></summary>

**Filters understood:** contains beef

**Answer:**

> Here are a few slow-cooker beef stews that fit your request:
>
> - Autumn Beef Stew: A hearty dish with a rich blend of vegetables and herbs, cooked in a crock-pot for 560 minutes. Each serving contains 673 kcal and 77% of the daily protein value.
> - Beef Stew for Two Slow Cooker: A healthier option with 475 kcal per serving, featuring beef stew meat, potatoes, and carrots, cooked in a slow cooker for 375 minutes.
> - Goulashy Beef Stew for the Slow Cooker: A simpler recipe with fewer ingredients, taking 430 minutes to cook and offering 566 kcal per serving.
> - Beef Burgundy for the Slow Cooker: A more complex and flavorful option with 718 kcal per serving, cooked for 570 minutes.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | Autumn beef stew | 560 min | 673 | red potatoes, carrot, onion, lean stewing beef, butter, flour … |
| ✓ cited | Beef stew for two slow cooker | 375 min | 475 | all-purpose flour, kosher salt, ground black pepper, onion powder, garlic powder, beef stew meat … |
|  | Beef stew with sun dried tomatoes | 500 min | 829 | sun-dried tomato, beef stew meat, red potatoes, onion, garlic cloves, carrots … |
| ✓ cited | Goulashy beef stew for the slow cooker | 430 min | 566 | boneless beef cubes, celery, carrots, onions, reduced-sodium fat-free beef broth, frozen baby peas … |
| ✓ cited | Beef burgundy for the slow cooker | 570 min | 718 | bacon, beef stew meat, salt & fresh ground pepper, onion, carrots, garlic cloves … |

</details>

<details class="replay" markdown>
<summary><b>A salad with quinoa and feta</b> <span class="tag">declined</span> <span class="tag">7 ms</span></summary>

**Filters understood:** contains quinoa, contains feta

**Answer:**

> No recipe in the collection matches all of these constraints: contains quinoa; contains feta. Try relaxing one of them.

</details>

<details class="replay" markdown>
<summary><b>What can I cook with leftover rice?</b> <span class="tag">answered</span> <span class="tag">773 ms</span></summary>

**Filters understood:** contains rice

**Answer:**

> You can use leftover rice to make leftover rice pudding, leftover chicken spinach and yellow pepper rice, or cheddar rice souffle.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | Leftover rice pudding | 30 min | 418 | rice, milk, sugar, salt, nutmeg, vanilla … |
| ✓ cited | Leftover chicken spinach and yellow pepper rice | 30 min | 486 | olive oil, yellow pepper, medium-grain white rice, white wine, chicken stock, cooked chicken … |
| ✓ cited | Cheddar rice souffle leftover rice | 35 min | 434 | butter, cheddar cheese, milk, white rice, salt, dry mustard … |
|  | Cheesy chicken rice casserole | 40 min | 208 | cooked rice, chicken, fresh tomato, bell peppers, green onions, fresh basil … |
|  | Chinese rice cakes | 12 min | 25 | fried rice, egg, flour, oil |

</details>

<details class="replay" markdown>
<summary><b>A pizza with peppers</b> <span class="tag">answered</span> <span class="tag">1.1 s</span></summary>

**Filters understood:** contains peppers

**Answer:**

> Here are some pizza options with peppers that you might enjoy:
>
> - Cheese and Pepperoni Pizza Supreme uses plum tomatoes and pepperoncini peppers.
> - Canadian Bacon Mushroom and Peppers Pizza includes green bell peppers.
> - Artichoke and Red Pepper Pizza features red bell peppers among its ingredients.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | Cheese and pepperoni pizza supreme | 27 min | 353 | boboli pizza crusts, pizza sauce, pepperoni, button mushroom, plum tomatoes, pepperoncini peppers … |
|  | Beef pizza casserole with pizza crust | 55 min | 533 | ground beef, dried chili pepper flakes, onions, garlic, green bell pepper, dried italian seasoning … |
| ✓ cited | Canadian bacon mushroom and peppers pizza | 30 min | 275 | italian bread, pizza sauce, part-skim mozzarella cheese, canadian bacon, fresh mushrooms, green bell peppers … |
|  | 3 c s and a p pizza | 30 min | 114 | pizza dough, prosciutto, roasted red pepper, alfredo sauce, pizza sauce, fresh basil … |
| ✓ cited | Artichoke and red pepper pizza | 0 min | 3577 | boboli thin pizza shell, olive oil, red bell pepper, dried basil, dried oregano, garlic … |

</details>

<details class="replay" markdown>
<summary><b>How do I change a car tyre?</b> <span class="tag">declined</span> <span class="tag">22 ms</span></summary>

**Answer:**

> I couldn't find any recipe related to that question in the collection.

</details>

<details class="replay" markdown>
<summary><b>Write me a poem about the sea</b> <span class="tag">declined</span> <span class="tag">19 ms</span></summary>

**Answer:**

> I couldn't find any recipe related to that question in the collection.

</details>

<details class="replay" markdown>
<summary><b>A vegan cheesecake that uses bacon</b> <span class="tag">declined</span> <span class="tag">20 ms</span></summary>

**Filters understood:** vegan, contains bacon

**Answer:**

> No recipe in the collection matches all of these constraints: contains bacon; tagged vegan. Try relaxing one of them.

</details>

<details class="replay" markdown>
<summary><b>Gluten-free bread without eggs</b> <span class="tag">answered</span> <span class="tag">998 ms</span></summary>

**Filters understood:** gluten-free, no eggs

**Answer:**

> The recipe for best banana bread no egg no milk gluten free fits your request. This bread takes 60 minutes to prepare and provides 411 kcal per serving, with protein making up 3% of the Daily Value. The ingredients include butter, sugar, gluten-free flour, baking soda, salt, bananas, pure vanilla extract, and chocolate chips.

| | Recipe | Time | kcal | Main ingredients |
|---|---|---|---|---|
| ✓ cited | Best banana bread no egg no milk gluten free | 60 min | 411 | butter, sugar, gluten-free flour, baking soda, salt, bananas … |
|  | Amazingly easy grain free biscuits rolls | 25 min | 212 | chickpea flour, tapioca starch, baking powder, salt, sugar, almond milk … |
|  | All purpose gluten free flour | 5 min | 512 | rice flour, potato starch, tapioca flour, xanthan gum |
|  | Baked cereal squares gluten free | 25 min | 142 | gluten-free flour, brown rice flour, flax seed meal, cornmeal, nonfat dry milk powder, dry active yeast … |
|  | Basic cake or muffin mix wheat and egg free | 40 min | 157 | gluten-free flour, salt, baking powder, caster sugar, butter, puree … |

</details>

<small>Recipe data: Food.com, collected by Majumder et al., EMNLP 2019. Only recipe facts are shown here.</small>

## How it works

- **One record per recipe** with structured fields (time, nutrition, tags, ingredients).
- **Constraints parsed from the question** ("under 30 minutes", "gluten-free", "uses flour and milk") become hard filters.
- **Hybrid search**: BM25 plus dense embeddings (bge-small), fused, then an off-topic guard that declines questions no recipe can answer.
- **Grounded answers**: a 7B instruction model writes the answer and must cite the recipes it used; citations are checked.
- An evaluation harness with a development set and a blind set written after tuning.

## Results

On 50,000 recipes, top 5 results, a blind set of 20 questions written after all tuning and run once:

- **0.85** of the results meet every constraint in the question
- **0.80** known-item recall
- **100%** of off-topic questions declined, with a median retrieval time of about 30 ms

With the language model on top: every citation points to a retrieved recipe, every cited recipe meets the
constraints, and every unanswerable question is declined, at about 1.1 s per answer.

## Origin

It started as the project for the Natural Language Processing course of my M.Sc.
at the University of Padova.

