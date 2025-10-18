# ===== 메인 실행 코드 =====

def main():
    """메인 실행 함수"""
    
    # 1. API 키 입력 (실제 사용 시에는 환경변수나 시크릿 사용)
    print("🔑 라이엇 API 키를 입력하세요:")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ API 키가 필요합니다.")
        return
    
    # 2. 매니저 초기화
    print("\n🚀 시스템 초기화 중...")
    riot_api = RiotAPIManager(api_key)
    match_manager = MatchManager(riot_api)
    visualizer = MatchVisualizer(match_manager)
    
    print("✅ 시스템 초기화 완료!")
    
    # 3. 메뉴 시스템
    while True:
        print("\n" + "="*50)
        print("🎮 롤다방 내전 관리 시스템")
        print("="*50)
        print("1. 플레이어 추가")
        print("2. 내전 생성")
        print("3. 내전 목록 보기")
        print("4. 팀 밸런스 분석")
        print("5. 챔피언 마스터리 보기")
        print("6. 대시보드 보기")
        print("7. 내전 상태 변경")
        print("0. 종료")
        print("="*50)
        
        choice = input("선택하세요 (0-7): ").strip()
        
        if choice == '0':
            print("👋 프로그램을 종료합니다.")
            break
        elif choice == '1':
            add_player_menu(match_manager)
        elif choice == '2':
            create_match_menu(match_manager)
        elif choice == '3':
            show_matches_menu(match_manager)
        elif choice == '4':
            analyze_balance_menu(match_manager, visualizer)
        elif choice == '5':
            show_mastery_menu(match_manager, visualizer)
        elif choice == '6':
            visualizer.create_dashboard()
        elif choice == '7':
            update_status_menu(match_manager)
        else:
            print("❌ 잘못된 선택입니다.")

def add_player_menu(match_manager):
    """플레이어 추가 메뉴"""
    print("\n👤 플레이어 추가")
    print("-" * 30)
    
    game_name = input("게임 이름: ").strip()
    tag_line = input("태그라인: ").strip()
    
    if not game_name or not tag_line:
        print("❌ 게임 이름과 태그라인을 모두 입력해주세요.")
        return
    
    player = match_manager.add_player(game_name, tag_line)
    if player:
        print(f"\n✅ 플레이어 정보:")
        print(f"  • 이름: {player['game_name']}#{player['tag_line']}")
        print(f"  • 레벨: {player['summoner_level']}")
        if player.get('league'):
            league = player['league']
            print(f"  • 티어: {league['tier']} {league['rank']} ({league['leaguePoints']}LP)")
            print(f"  • 승률: {league['wins']}/{league['losses']} ({league['wins']/(league['wins']+league['losses'])*100:.1f}%)")
        else:
            print("  • 티어: 언랭크")

def create_match_menu(match_manager):
    """내전 생성 메뉴"""
    print("\n🏆 내전 생성")
    print("-" * 30)
    
    match_id = input("내전 ID: ").strip()
    if not match_id:
        print("❌ 내전 ID를 입력해주세요.")
        return
    
    print("내전 종류:")
    print("1. 소프트 피어리스")
    print("2. 하드 피어리스") 
    print("3. 하이퍼 피어리스")
    
    type_choice = input("선택 (1-3): ").strip()
    type_map = {'1': 'soft', '2': 'hard', '3': 'hyper'}
    match_type = type_map.get(type_choice, 'soft')
    
    host = input("진행자: ").strip()
    if not host:
        print("❌ 진행자를 입력해주세요.")
        return
    
    print("\n플레이어 추가 (게임이름#태그라인 형식, 빈 줄로 종료):")
    players = []
    while True:
        player = input(f"플레이어 {len(players)+1}: ").strip()
        if not player:
            break
        if '#' not in player:
            print("❌ 게임이름#태그라인 형식으로 입력해주세요.")
            continue
        players.append(player)
    
    if len(players) < 2:
        print("❌ 최소 2명의 플레이어가 필요합니다.")
        return
    
    match = match_manager.create_match(match_id, match_type, host, players)
    print(f"\n✅ 내전 생성 완료!")
    print(f"  • ID: {match['id']}")
    print(f"  • 종류: {match['type']}")
    print(f"  • 참가자: {len(match['players'])}명")

def show_matches_menu(match_manager):
    """내전 목록 보기 메뉴"""
    print("\n📋 내전 목록")
    print("-" * 30)
    
    if not match_manager.matches:
        print("❌ 등록된 내전이 없습니다.")
        return
    
    for i, match in enumerate(match_manager.matches, 1):
        print(f"{i}. {match['id']} ({match['type']}) - {match['status']} - {len(match['players'])}명")

def analyze_balance_menu(match_manager, visualizer):
    """팀 밸런스 분석 메뉴"""
    print("\n⚖️ 팀 밸런스 분석")
    print("-" * 30)
    
    if not match_manager.matches:
        print("❌ 등록된 내전이 없습니다.")
        return
    
    print("내전 목록:")
    for i, match in enumerate(match_manager.matches, 1):
        print(f"{i}. {match['id']} ({match['type']}) - {len(match['players'])}명")
    
    try:
        choice = int(input("분석할 내전 번호: ")) - 1
        if 0 <= choice < len(match_manager.matches):
            match = match_manager.matches[choice]
            balance = match_manager.analyze_team_balance(match['id'])
            
            print(f"\n📊 {match['id']} 팀 밸런스 분석:")
            print(f"  • 블루팀 점수: {balance['blue_score']:.2f}")
            print(f"  • 레드팀 점수: {balance['red_score']:.2f}")
            print(f"  • 밸런스 비율: {balance['balance_ratio']:.2f}")
            print(f"  • 밸런스 상태: {'균형' if balance['is_balanced'] else '불균형'}")
            
            # 시각화
            visualizer.plot_team_balance(match['id'])
        else:
            print("❌ 잘못된 번호입니다.")
    except ValueError:
        print("❌ 숫자를 입력해주세요.")

def show_mastery_menu(match_manager, visualizer):
    """챔피언 마스터리 보기 메뉴"""
    print("\n🏆 챔피언 마스터리 보기")
    print("-" * 30)
    
    if not match_manager.players:
        print("❌ 등록된 플레이어가 없습니다.")
        return
    
    print("플레이어 목록:")
    for i, (key, player) in enumerate(match_manager.players.items(), 1):
        print(f"{i}. {player['game_name']}#{player['tag_line']}")
    
    try:
        choice = int(input("플레이어 번호: ")) - 1
        player_list = list(match_manager.players.items())
        if 0 <= choice < len(player_list):
            player_key, player = player_list[choice]
            visualizer.plot_champion_mastery(player['game_name'])
        else:
            print("❌ 잘못된 번호입니다.")
    except ValueError:
        print("❌ 숫자를 입력해주세요.")

def update_status_menu(match_manager):
    """내전 상태 변경 메뉴"""
    print("\n🔄 내전 상태 변경")
    print("-" * 30)
    
    if not match_manager.matches:
        print("❌ 등록된 내전이 없습니다.")
        return
    
    print("내전 목록:")
    for i, match in enumerate(match_manager.matches, 1):
        print(f"{i}. {match['id']} - {match['status']}")
    
    try:
        choice = int(input("변경할 내전 번호: ")) - 1
        if 0 <= choice < len(match_manager.matches):
            match = match_manager.matches[choice]
            print(f"\n현재 상태: {match['status']}")
            print("새로운 상태:")
            print("1. open (모집중)")
            print("2. in_progress (진행중)")
            print("3. completed (완료)")
            print("4. closed (종료)")
            
            status_choice = input("선택 (1-4): ").strip()
            status_map = {'1': 'open', '2': 'in_progress', '3': 'completed', '4': 'closed'}
            new_status = status_map.get(status_choice)
            
            if new_status:
                match_manager.update_match_status(match['id'], new_status)
                print(f"✅ 내전 상태가 {new_status}로 변경되었습니다.")
            else:
                print("❌ 잘못된 선택입니다.")
        else:
            print("❌ 잘못된 번호입니다.")
    except ValueError:
        print("❌ 숫자를 입력해주세요.")

# 실행
if __name__ == "__main__":
    main()

print("✅ 메인 실행 코드 정의 완료!")
