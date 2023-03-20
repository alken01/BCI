//
//  ContentView.swift
//  BCI
//
//  Created by Alken Rrokaj on 19/03/2023.
//

import SwiftUI

struct ContentView: View {
    @State private var selectedOption: SidebarOption? = .option1

    var body: some View {
        NavigationView {
            Sidebar(selectedOption: $selectedOption)
            Group {
                switch selectedOption {
                case .option1:
                    Option1View()
                case .option2:
                    Option2View()
                case .option3:
                    Option3View()
                case .none:
                    Text("Select an option from the sidebar")
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }
}

struct Sidebar: View {
    @Binding var selectedOption: SidebarOption?

    var body: some View {
        List(selection: $selectedOption) {
            NavigationLink(destination: Option1View()) {
                Label("Option 1", systemImage: "1.circle")
            }
            .tag(SidebarOption.option1)
            
            NavigationLink(destination: Option2View()) {
                Label("Option 2", systemImage: "2.circle")
            }
            .tag(SidebarOption.option2)
            
            NavigationLink(destination: Option3View()) {
                Label("Option 3", systemImage: "3.circle")
            }
            .tag(SidebarOption.option3)
        }
        .listStyle(SidebarListStyle())
        .frame(minWidth: 150, idealWidth: 200, maxWidth: 250)
    }
}

enum SidebarOption: Hashable {
    case option1, option2, option3
}

struct Option1View: View {
    var body: some View {
        Text("Option 1 content")
    }
}

struct Option2View: View {
    var body: some View {
        Text("Option 2 content")
    }
}

struct Option3View: View {
    var body: some View {
        Text("Option 3 content")
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
